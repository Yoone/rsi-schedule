from PIL import Image


__all__ = ['get_blocks']


EMPTY_RGB = (255, 255, 255)


def is_line_color(im, start, length, rgb, vertical=False, invert_color=False):
    x_start, y_start = start
    x_end = x_start
    y_end = y_start
    if vertical:
        x_end += length
        y_end + 1
    else:
        x_end += 1
        y_end += length

    width, height = im.size
    for x in range(x_start, min(x_end, width)):
        for y in range(y_start, min(y_end, height)):
            c = im.getpixel((x, y))
            if invert_color:
                if c == rgb:
                    return False
            elif c != rgb:
                return False

    return True


def table_corner(im):
    line_len = 15  # 5px at (255, 255, 255) around corner
    corner_decal = 2

    width, height = im.size
    for x in range(width - 1):
        for y in range(height - 1):
            px = (x, y)
            px_c = (x + 1, y + 1)

            c = is_line_color(im, px, line_len, EMPTY_RGB)
            c = c and is_line_color(im, px, line_len, EMPTY_RGB, vertical=True)
            c = c and is_line_color(im, px_c, line_len, EMPTY_RGB, invert_color=True)
            c = c and is_line_color(im, px_c, line_len, EMPTY_RGB, vertical=True, invert_color=True)

            if c:
                return (px_c[0] + corner_decal, px_c[1] + corner_decal)


def next_vertical_sep(im, pos, h_decal):
    sep_threshold = 225  # Needs to be greater or equal
    add_h = 20  # Arbitrary number of pixels to avoid a color too bright (because of resizing)

    for y in range(pos[1], im.size[1] - 1):
        r, g, b = im.getpixel((pos[0] + h_decal + add_h, y))
        mean_color = (r + g + b) / 3
        if mean_color >= sep_threshold:
            return (pos[0], y)


def horizontal_decal(im, pos):
    x, y = pos
    try:
        while im.getpixel((x, y)) == EMPTY_RGB:
            x += 1
        return x - pos[0]
    except IndexError:
        return None


def get_blocks(im_file):
    bl_width = 300  # 300px
    bl_sep_err = 3  # 3px to be safe (images are clearly resized)
    right_padding = 100  # 100px on the right side of the image
    sz_mult = 4  # Size *= 4 (in order to work well with an OCR)

    im = Image.open(im_file).convert('RGB')
    blocks = []

    corner = table_corner(im)
    while corner:
        if is_line_color(im, corner, im.size[0] - right_padding, EMPTY_RGB):
            break

        hdec = horizontal_decal(im, corner)
        if hdec is None:
            break

        sep_x, sep_y = next_vertical_sep(im, corner, hdec)
        while sep_y - corner[1] <= bl_sep_err:
            sep_x, sep_y = next_vertical_sep(im, (sep_x, sep_y + 1), hdec)

        block = im.crop((corner[0] + hdec, corner[1], sep_x + bl_width + hdec, sep_y))
        w, h = block.size
        resized = block.resize((w * sz_mult, h * sz_mult), Image.ANTIALIAS)
        blocks.append(resized)

        corner = (sep_x, sep_y + 1)

    return blocks


if __name__ == '__main__':
    # FIXME: Rudimentary manual testing
    import sys
    import os
    im_file = sys.argv[1]
    test_dir = sys.argv[2]
    for i, block in enumerate(get_blocks(im_file)):
        block.save(os.path.join(test_dir, 'block{}.png'.format(i)))
