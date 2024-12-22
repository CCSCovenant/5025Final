#version 330 core

in GS_OUT {
    float param;   // GS中插值输出的 param
} fs_in;

uniform vec3 uColor;  // 每条笔画的整体颜色 (示例：由 Python 动态传入)

out vec4 fragColor;

void main()
{
    // 简单使用 uniform 颜色，也可以结合 param 做颜色渐变
    fragColor = vec4(uColor, 1.0);
}
