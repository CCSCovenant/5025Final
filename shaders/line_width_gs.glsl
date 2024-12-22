#version 330 core

layout(lines) in;                               // 输入拓扑：线段
layout(triangle_strip, max_vertices = 4) out;   // 输出拓扑：三角带，每条线段最多生成 4 个顶点

in VS_OUT {
    vec3 worldPos;
    float param;
} gs_in[];  // 两个端点的数据

// 传给片元着色器
out GS_OUT {
    float param;
} gs_out;

uniform mat4 uMVP;
uniform float uBaseWidth;    // 基础线宽
uniform float uScaleFactor;  // 线宽缩放系数

void main()
{
    // 1) 取出线段两个端点和各自的 param
    vec3 p0 = gs_in[0].worldPos;
    vec3 p1 = gs_in[1].worldPos;
    float param0 = gs_in[0].param;
    float param1 = gs_in[1].param;

    // 2) 分别计算两端点在 Clip Space 下的坐标
    vec4 clip0 = uMVP * vec4(p0, 1.0);
    vec4 clip1 = uMVP * vec4(p1, 1.0);

    // 3) 在 NDC 中求线段方向
    vec2 ndcPos0 = clip0.xy / clip0.w;
    vec2 ndcPos1 = clip1.xy / clip1.w;
    vec2 dir = normalize(ndcPos1 - ndcPos0);

    // 与方向垂直的向量
    vec2 perp = vec2(-dir.y, dir.x);

    // 4) 计算两端的线宽 (示例：width = baseWidth + param * scaleFactor)
    float w0 = uBaseWidth + param0 * uScaleFactor;
    float w1 = uBaseWidth + param1 * uScaleFactor;

    // 5) 在透视投影下，为了让线宽看起来近似恒定于屏幕像素，需要在 clip.w 上做适当缩放
    vec2 offset0 = perp * w0 * clip0.w;
    vec2 offset1 = perp * w1 * clip1.w;

    // 6) 生成四个顶点 (p0-left, p0-right, p1-left, p1-right)
    // --- p0 left ---
    {
        vec4 outClip = clip0;
        outClip.xy += offset0;
        gl_Position = outClip;
        gs_out.param = param0;
        EmitVertex();
    }
    // --- p0 right ---
    {
        vec4 outClip = clip0;
        outClip.xy -= offset0;
        gl_Position = outClip;
        gs_out.param = param0;
        EmitVertex();
    }
    // --- p1 left ---
    {
        vec4 outClip = clip1;
        outClip.xy += offset1;
        gl_Position = outClip;
        gs_out.param = param1;
        EmitVertex();
    }
    // --- p1 right ---
    {
        vec4 outClip = clip1;
        outClip.xy -= offset1;
        gl_Position = outClip;
        gs_out.param = param1;
        EmitVertex();
    }

    EndPrimitive();
}
