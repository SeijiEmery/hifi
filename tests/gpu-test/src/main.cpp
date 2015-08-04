//
//  main.cpp
//  tests/gpu-test/src
//
//  Copyright 2015 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

#include <unordered_map>
#include <memory>

#include <glm/glm.hpp>

#include <QApplication>
#include <QDir>
#include <QElapsedTimer>
#include <QFile>
#include <QImage>
#include <QLoggingCategory>

#include <gpu/Context.h>
#include <gpu/Batch.h>
#include <gpu/Stream.h>
#include <gpu/StandardShaderLib.h>
//#include <shared/ViewFrustrum.h>

#include <gpu/GLBackend.h>

//#include <QOpenGLBuffer>
#include <QOpenGLContext>
//#include <QOpenGLDebugLogger>
//#include <QOpenGLShaderProgram>
//#include <QOpenGLTexture>
//#include <QOpenGLVertexArrayObject>
#include <QResizeEvent>
#include <QTime>
#include <QTimer>
#include <QWindow>
#include <cstdio>
#include <PathUtils.h>

#include "gputest_shaders.h"


class RateCounter {
    std::vector<float> times;
    QElapsedTimer timer;
public:
    RateCounter() {
        timer.start();
    }

    void reset() {
        times.clear();
    }

    unsigned int count() const {
        return times.size() - 1;
    }

    float elapsed() const {
        if (times.size() < 1) {
            return 0.0f;
        }
        float elapsed = *times.rbegin() - *times.begin();
        return elapsed;
    }

    void increment() {
        times.push_back(timer.elapsed() / 1000.0f);
    }

    float rate() const {
        if (elapsed() == 0.0f) {
            return NAN;
        }
        return (float) count() / elapsed();
    }
};


const QString& getQmlDir() {
    static QString dir;
    if (dir.isEmpty()) {
        QDir path(__FILE__);
        path.cdUp();
        dir = path.cleanPath(path.absoluteFilePath("../../../interface/resources/qml/")) + "/";
        qDebug() << "Qml Path: " << dir;
    }
    return dir;
}

#define MOVE_PARAM(name) decltype(name) && name

struct BasicModel {
    gpu::PipelinePointer pipeline;
//    gpu::BufferPointer vertexBuffer;
//    gpu::BufferPointer indexBuffer;
//    gpu::BufferPointer normalBuffer;
    
    gpu::BufferView vertices;
    gpu::BufferView normals;
    gpu::BufferPointer indices;

    gpu::Stream::FormatPointer format;
    
    BasicModel (MOVE_PARAM(pipeline), MOVE_PARAM(vertices), MOVE_PARAM(normals), MOVE_PARAM(indices), MOVE_PARAM(format))
        : pipeline(pipeline), vertices(vertices), normals(normals), indices(indices), format(format) {}
    
//    BasicModel (gpu::PipelinePointer && pipeline, gpu::BufferPointer && buffer, gpu::Stream::FormatPointer && format)
//        : pipeline(pipeline), buffer(buffer), format(format) {}
};
typedef std::shared_ptr<BasicModel> BasicModelPointer;
#undef MOVE_PARAM

BasicModelPointer makeCube () {
    // Axis-aligned cube, facing the user at +z
    // coords == binary mapping of each index, with z inverted (front face faces camera,
    // instead of away from the camera)
    //
    //           -x,+y,-z ----------- +x,+y,-z
    //        ___--- |           ___---   |
    //   -x,+y,+z --------- +x,+y,+z      |
    //       |       |          |         |
    //       |       |          |         |
    //       |       |          |         |
    //       |       |          |         |
    //       |   -x,-y,-z ------|---- +x,-y,-z
    //       | ___---           | ___----
    //   -x,-y,+z --------- +x,-y,+z
    //
    float s = 1.0f;
    const glm::vec3 raw_verts[8] = {
    //     x,  y,  z
        { -s, -s, +s }, // 0b000    0x0
        { +s, -s, +s }, // 0b001    0x1
        { -s, +s, +s }, // 0b010    0x2
        { +s, +s, +s }, // 0b011    0x3
        { -s, -s, -s }, // 0b100    0x4
        { +s, -s, -s }, // 0b101    0x5
        { -s, +s, -s }, // 0b110    0x6
        { +s, +s, -s }  // 0b111    0x7
    };
    const glm::vec3 raw_normals[6] = {
        { 0.0f, 0.0f, +1.0f },  // x > 0:   1, 3, 5, 7      (N 0)
        { 0.0f, 0.0f, -1.0f },  // x < 0:   0, 2, 4, 6      (N 1)
        { 0.0f, +1.0f, 0.0f },  // y > 0:   2, 3, 6, 7      (N 2)
        { 0.0f, -1.0f, 0.0f },  // y < 0:   0, 1, 4, 5      (N 3)
        { +1.0f, 0.0f, 0.0f },  // z > 0:   0, 1, 2, 3      (N 4)
        { -1.0f, 0.0f, 0.0f }   // z < 0:   4, 5, 6, 7      (N 5)
    };
    
    const glm::vec3 cube_verts[24] = {
        raw_verts[1], raw_verts[3], raw_verts[5], raw_verts[7],
        raw_verts[0], raw_verts[2], raw_verts[4], raw_verts[6],
        raw_verts[2], raw_verts[3], raw_verts[6], raw_verts[7],
        raw_verts[0], raw_verts[1], raw_verts[4], raw_verts[5],
        raw_verts[0], raw_verts[1], raw_verts[2], raw_verts[3],
        raw_verts[4], raw_verts[5], raw_verts[6], raw_verts[7]
    };
    const glm::vec3 cube_normals[24] = {
        raw_normals[0], raw_normals[0], raw_normals[0], raw_normals[0],
        raw_normals[1], raw_normals[1], raw_normals[1], raw_normals[1],
        raw_normals[2], raw_normals[2], raw_normals[2], raw_normals[2],
        raw_normals[3], raw_normals[3], raw_normals[3], raw_normals[3],
        raw_normals[4], raw_normals[4], raw_normals[4], raw_normals[4],
        raw_normals[5], raw_normals[5], raw_normals[5], raw_normals[5]
    };
    
    int16_t cube_indices_tris[36];
    for (int i = 0, k = 0; i < 36; k += 4) {
        cube_indices_tris[i++] = k + 0;
        cube_indices_tris[i++] = k + 3;
        cube_indices_tris[i++] = k + 1;
        cube_indices_tris[i++] = k + 0;
        cube_indices_tris[i++] = k + 2;
        cube_indices_tris[i++] = k + 3;
    }
    
//  const int16_t cube_indices_tris[36] {
//      0, 3, 1,    0, 2, 3,
//  };

//    const glm::vec3 cube_normals[] = {
//        { 0.0f, 0.0f, 1.0f },
//        { 0.0f, 0.0f, 1.0f },
//        { 0.0f, 0.0f, 1.0f },
//        { 0.0f, 0.0f, 1.0f },
//        { -1.0f, 0.0f, 0.0f },
//        { -1.0f, 0.0f, 0.0f },
//        { -1.0f, 0.0f, 0.0f },
//        { -1.0f, 0.0f, 0.0f },
//    };
//    const int16_t cube_indices[] = {
//        3, 1, 0,    2, 3, 0,
//        6, 2, 0,    4, 6, 0,
//    };
    
    gpu::Stream::FormatPointer format = std::make_shared<gpu::Stream::Format>();
    format->setAttribute(gpu::Stream::POSITION, gpu::Stream::POSITION, gpu::Element::VEC3F_XYZ);
    format->setAttribute(gpu::Stream::NORMAL, gpu::Stream::NORMAL, gpu::Element::VEC3F_XYZ);
    
    auto vertexBuffer = std::make_shared<gpu::Buffer>(24 * sizeof(glm::vec3), (gpu::Byte*)cube_verts);
    auto normalBuffer = std::make_shared<gpu::Buffer>(24 * sizeof(glm::vec3), (gpu::Byte*)cube_normals);
    gpu::BufferPointer indexBuffer  = std::make_shared<gpu::Buffer>(36 * sizeof(int16_t), (gpu::Byte*)cube_indices_tris);
    
    auto positionElement = format->getAttributes().at(gpu::Stream::POSITION)._element;
    auto normalElement = format->getAttributes().at(gpu::Stream::NORMAL)._element;
    
    gpu::BufferView vertexView { vertexBuffer, positionElement };
    gpu::BufferView normalView { normalBuffer, normalElement };
    
    // Create shaders
    auto vs = gpu::ShaderPointer(gpu::Shader::createVertex(basicVertexShader()));
    auto fs = gpu::ShaderPointer(gpu::Shader::createPixel(basicFragmentShader()));
    auto shader = gpu::ShaderPointer(gpu::Shader::createProgram(vs, fs));
    
    gpu::Shader::BindingSet bindings;
        
    if (!gpu::Shader::makeProgram(*shader, bindings)) {
        printf("Could not compile shader\n");
        if (!vs)
            printf("bad vertex shader\n");
        if (!fs)
            printf("bad fragment shader\n");
        if (!shader)
            printf("bad shader program\n");
        exit(-1);
    }
    
    auto state = std::make_shared<gpu::State>();
//    state->setAntialiasedLineEnable(true);
    state->setMultisampleEnable(true);
    state->setDepthTest({ true });
    auto pipeline = gpu::PipelinePointer(gpu::Pipeline::create(shader, state));

    return std::make_shared<BasicModel>(
        std::move(pipeline),
        std::move(vertexView),
        std::move(normalView),
        std::move(indexBuffer),
        std::move(format)
    );
}

void renderCube(gpu::Batch & batch, const BasicModel & cube) {
    
    batch.setPipeline(cube.pipeline);
    batch.setInputFormat(cube.format);
    batch.setInputBuffer(gpu::Stream::POSITION, cube.vertices);
    batch.setInputBuffer(gpu::Stream::NORMAL, cube.normals);
    batch.setIndexBuffer(gpu::INT16, cube.indices, 0);
//    batch.drawIndexed(gpu::TRIANGLES, 12);
    batch.draw(gpu::TRIANGLES, 24);
}

// Create a simple OpenGL window that renders text in various ways
class QTestWindow : public QWindow {
    Q_OBJECT

    QOpenGLContext* _qGlContext{ nullptr };
    QSize _size;
    
    gpu::ContextPointer _context;
    gpu::PipelinePointer _pipeline;
    BasicModelPointer _cubeModel;
    //TextRenderer* _textRenderer[4];
    RateCounter fps;

protected:
    void renderText();

private:
    void resizeWindow(const QSize& size) {
        _size = size;
    }

public:
    QTestWindow() {
        setSurfaceType(QSurface::OpenGLSurface);

        QSurfaceFormat format;
        // Qt Quick may need a depth and stencil buffer. Always make sure these are available.
        format.setDepthBufferSize(16);
        format.setStencilBufferSize(8);
        format.setVersion(4, 5);
        format.setProfile(QSurfaceFormat::OpenGLContextProfile::CompatibilityProfile);
        format.setOption(QSurfaceFormat::DebugContext);

        setFormat(format);

        _qGlContext = new QOpenGLContext;
        _qGlContext->setFormat(format);
        _qGlContext->create();

        show();
        makeCurrent();

        gpu::Context::init<gpu::GLBackend>();
        _context = std::make_shared<gpu::Context>();
        
        // Clear screen
        gpu::Batch batch;
        batch.clearColorFramebuffer(gpu::Framebuffer::BUFFER_COLORS, { 1.0, 0.0, 0.5, 1.0 });
        _context->render(batch);
        
        _cubeModel = makeCube();
        
//        makeCurrent();
//        _context->syncCache();

        setFramePosition(QPoint(-1000, 0));
        resize(QSize(800, 600));
    }

    virtual ~QTestWindow() {
    }

    void draw();
    void makeCurrent() {
        _qGlContext->makeCurrent(this);
    }

protected:

    void resizeEvent(QResizeEvent* ev) override {
        resizeWindow(ev->size());
    }
};

#ifndef SERIF_FONT_FAMILY
#define SERIF_FONT_FAMILY "Times New Roman"
#endif

//static const wchar_t* EXAMPLE_TEXT = L"Hello";
//static const wchar_t* EXAMPLE_TEXT = L"\xC1y Hello 1.0\ny\xC1 line 2\n\xC1y";
static const glm::uvec2 QUAD_OFFSET(10, 10);

static const glm::vec3 COLORS[4] = {
    { 1.0, 1.0, 1.0 },
    { 0.5, 1.0, 0.5 },
    { 1.0, 0.5, 0.5 },
    { 0.5, 0.5, 1.0 }
};


void QTestWindow::draw() {
    if (!isVisible()) {
        return;
    }

    makeCurrent();
    
    gpu::Batch batch;
    static int frameNum = 0;
    frameNum++;
    float t = frameNum / 120.0f;
    
    float k = (frameNum % 120) / 120;
    float ks = glm::sin(glm::pi<float>() * 2.0f * k);

    batch.clearColorFramebuffer(gpu::Framebuffer::BUFFER_COLORS, { 0.1, 0.1, 0.1, 1.0 });
//    batch.clearDepthFramebuffer(-10000.0f);
//    batch.clearColorFramebuffer(gpu::Framebuffer::BUFFER_COLORS, { 1.0, float(frameNum % 60)/60.0f, 0.5, 1.0 });
    
    batch.setViewportTransform({ 0, 0, _size.width() * devicePixelRatio(), _size.height() * devicePixelRatio() });
    
    
    
    // camera at x: 5 * sin(t)
    //           y: 1,
    //           z: +10
    // obj at (0, 0, 0)
    // camera is looking at obj (using glm::lookAt)
    
    glm::vec3 up { 0.0f, 1.0f, 0.0f };
    glm::vec3 unitscale { 1.0f };
    
    float cube_angle = 0.0f;
//    glm::vec3 cube_pos {
//        0.0f,
//        0.0f,
//        0.0f
//    };
    glm::vec3 cube_pos {
        20.0f * cos(t * 5.0f),
        10.0f * sin(t * 2.5f) + 1.0f,
        -15.0f + float(int(t * int(1e3)) % int(1e4)) / 1e3
    };
    
    //    float cube_angle = 360.0f * k * 1.25 + 120.0f * k * 0.1f;
//    glm::quat cube_rotation = glm::angleAxis(glm::radians(cube_angle), up);
    glm::quat cube_rotation;
    Transform cube_transform { cube_rotation, unitscale, cube_pos };
    
//    glm::vec3 cam_pos { 0.0f, 0.0f, -10.0f };
    glm::vec3 cam_pos { 5.0f * sin(t * 0.1f), 1.0f, -10.0f };
    glm::quat cam_rotation = glm::quat_cast(glm::lookAt(cam_pos, cube_pos, up));
    cam_rotation.w = -cam_rotation.w;
    Transform cam_transform { cam_rotation, unitscale, cam_pos };
    
    float fov_degrees = 120.0f;
//    float aspect_ratio = _size.height() / (_size.width() || 1.0f);
    float aspect_ratio = 16.0f / 9.0f;
    float near_clip = 0.1f;
    float far_clip = 1000.0f;
    auto projection = glm::perspective(glm::radians(fov_degrees), aspect_ratio, near_clip, far_clip);
    
    batch.setProjectionTransform(projection);
    batch.setViewTransform(cam_transform);
    batch.setModelTransform(cube_transform);
    
    batch.setModelTransform(Transform().setTranslation({ 20.0f * cos(t * 5.0f), 10.0f * sin(t * 2.5f + 1.0f), -15.0f + float(int(t * 1000) % 10000) / 1e3f}));
//    batch.setPipeline(_pipeline);
//    batch.setInputBuffer(gpu::Stream::POSITION, _buffer, 0, 3);
//    batch.setInputFormat(_format);
//    batch.draw(gpu::TRIANGLES, 3);
    
    renderCube(batch, *_cubeModel);
    _context->render(batch);
//
////    gpu::Stream::Format format;
////    format.setAttribute(gpu::Stream::POSITION, gpu::Stream::POSITION, gpu::Element(gpu::Vec3, gpu::FLOAT, gpu::XYZ));
////    batch.setInputBuffer(gpu::Stream::POSITION, _trianglePosBuffer, )
    
    _qGlContext->swapBuffers(this);
   // glFinish();

    fps.increment();
    if (fps.elapsed() >= 2.0f) {
        qDebug() << "FPS: " << fps.rate() * 2.0f;  // This prints out the frames per 2 secs (ie. half of the actual fps)  bug...?
        fps.reset();
    }
}

int main(int argc, char** argv) {    
    QGuiApplication app(argc, argv);
    QTestWindow window;
    QTimer timer;
//    timer.setInterval(1000 / 120.0f);
    timer.setInterval(0);
    app.connect(&timer, &QTimer::timeout, &app, [&] {
        window.draw();
    });
    timer.start();
    app.exec();
    return 0;
}

#include "main.moc"
