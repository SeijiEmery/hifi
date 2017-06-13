//
//  FadeEffect.h
//  libraries/render-utils/src/
//
//  Created by Olivier Prat on 06/06/17.
//  Copyright 2017 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//
#ifndef hifi_FadeEffect_h
#define hifi_FadeEffect_h

#include <DependencyManager.h>
#include <gpu/Pipeline.h>
#include <render/ShapePipeline.h>

// Centralizes fade effect data and functions
class FadeEffect : public Dependency {
	SINGLETON_DEPENDENCY
public:

	FadeEffect();

	const gpu::TexturePointer getFadeMaskMap() const { return _fadeMaskMap; }

    void setScale(float value) { assert(value > 0.f); _invScale = 1.f / value; }
    float getScale() const { return 1.f / _invScale; }

    void setDuration(float seconds) { assert(seconds > 0.f); _duration = seconds; }
    float getDuration() const { return 1.f / _duration; }

    void setDebugEnabled(bool isEnabled) { _isDebugEnabled = isEnabled; }
	bool isDebugEnabled() const { return _isDebugEnabled; }

    void setDebugFadePercent(float value) { assert(value >= 0.f && value <= 1.f); _debugFadePercent = value; }
    float getDebugFadePercent() const { return _debugFadePercent; }

	render::ShapeKey::Builder getKeyBuilder(render::ShapeKey::Builder builder = render::ShapeKey::Builder()) const;

    void bindPerBatch(gpu::Batch& batch, int fadeMaskMapLocation = render::ShapePipeline::Slot::MAP::FADE_MASK) const;
    void bindPerBatch(gpu::Batch& batch, const gpu::PipelinePointer& pipeline) const;
    bool bindPerItem(gpu::Batch& batch, RenderArgs* args, glm::vec3 offset, quint64 startTime, bool isFading) const;
    bool bindPerItem(gpu::Batch& batch, const gpu::Pipeline* pipeline, glm::vec3 offset, quint64 startTime, bool isFading) const;

    float computeFadePercent(quint64 startTime) const;

private:

	gpu::TexturePointer _fadeMaskMap;
    float _invScale;
    float _duration;
	float _debugFadePercent;
	bool _isDebugEnabled;
};

#endif // hifi_FadeEffect_h
