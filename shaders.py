vertex_scene = b'''
#version 130
attribute vec4 position;
attribute vec4 color;

out vec4 vtx_color;

const float VOXEL_HEIGHT = 24.0;
const float VOXEL_Y_SIDE = 24.0;
const float VOXEL_X_SIDE = 48.0;

uniform vec2 screen_size;
uniform vec2 scroll_offset;

void main()
{

    gl_Position = vec4((position.x-position.y)/5.0,
                       (position.x+position.y+position.z*0.7)/10.0-0.5,
                       (position.x+position.y)/10.0,
                       position.w);
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

fragment_sprite = b'''
#version 130

uniform sampler2D tex;
varying vec4 vtx_color;
out vec4 FragColor;

void main()
{
    FragColor = texture2D(tex, vtx_color.xy);
}
'''
