vertex_scene = b'''
#version 130
attribute vec4 position;
attribute vec4 color;

out vec4 vtx_color;

const float VOXEL_HEIGHT = 24.0;
const float VOXEL_Y_SIDE = 24.0;
const float VOXEL_X_SIDE = 48.0;

void main()
{
    gl_Position = position;
    vtx_color = color;
}
'''

fragment_scene = b'''
#version 130

varying vec4 vtx_color;
out vec4 FragColor;

void main()
{
    FragColor = vtx_color;
}
'''
