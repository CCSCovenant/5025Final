#version 330 core

layout(location = 0) in vec3 inPosition;   // 笔画顶点的 3D 坐标
layout(location = 1) in float inParam;     // 用于线宽渐变的参数 (如距离、笔压、笔画进度等)

uniform mat4 uMVP;  // 模型-视图-投影矩阵

// 传给几何着色器的结构体
out VS_OUT {
    vec3 worldPos;
    float param;
} vs_out;

void main()
{
    vs_out.worldPos = inPosition;
    vs_out.param = inParam;

    // 先做 MVP 变换，把顶点送到 Clip Space
    gl_Position = uMVP * vec4(inPosition, 1.0);
}
