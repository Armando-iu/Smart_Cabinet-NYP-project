from machine import Pin, I2C
import ssd1306
import framebuf
from time import sleep

# OLED setup
i2c = I2C(sda=Pin(21), scl=Pin(22))
display = ssd1306.SSD1306_I2C(128, 64, i2c)


health = [
        0b00000111, 0b11100000,
        0b00000111, 0b11100000,
        0b00000111, 0b11100000,
        0b00000111, 0b11100000,
        0b00000111, 0b11100000,
        0b11111111, 0b11111111,
        0b11111111, 0b11111111,
        0b11111111, 0b11111111,
        0b11111111, 0b11111111,
        0b00000111, 0b11100000,
        0b00000111, 0b11100000,
        0b00000111, 0b11100000,
        0b00000111, 0b11100000,
        0b00000111, 0b11100000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        
    ]

heart_data = [
        0b00000000, 0b00000000,
        0b00000100, 0b00010000,
        0b00001110, 0b00111000,
        0b00011111, 0b11111100,
        0b00111111, 0b11111110,
        0b00111111, 0b11111110,
        0b00111111, 0b11111100,
        0b00011111, 0b11111000,
        0b00001111, 0b11110000,
        0b00000111, 0b11100000,
        0b00000011, 0b11000000,
        0b00000001, 0b10000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
    ]
temp_data = [
                    0b00000011, 0b00000000,
                    0b00000100, 0b10011000,
                    0b00000100, 0b10000000,
                    0b00000100, 0b10011100,
                    0b00000100, 0b10000000,
                    0b00000100, 0b10010000,
                    0b00000100, 0b10000000,
                    0b00000100, 0b10011100,
                    0b00000100, 0b10000000,
                    0b00000100, 0b10011000,
                    0b00000100, 0b10000000,
                    0b00001000,	0b01000000,
                    0b00010000,	0b00100000,
                    0b00100000,	0b00010000,
                    0b00100000,	0b00010000,
                    0b00100000,	0b00010000,
                    0b00100000,	0b00010000,
                    0b00010000,	0b00100000,
                    0b00001000,	0b01000000,
                    0b00000111,	0b10000000,
                    
                    
    ]


def select(rows,column):
    grid_width = 2
    grid_height = 2
    cell_size = 30
    cell_spacing = 1
    selected_row = rows    # Initially select the top-left cell
    selected_col = column

    # Calculate starting position
    start_x = (display.width // 2) - ((grid_width * cell_size + (grid_width - 1) * cell_spacing) // 2)
    start_y = (display.height // 2) - ((grid_height * cell_size + (grid_height - 1) * cell_spacing) // 2)

    while True:
        display.fill(0)  # Clear the screen

        # Draw the Grid
        for row in range(grid_height):
            for col in range(grid_width):
                x = start_x + col * (cell_size + cell_spacing)
                y = start_y + row * (cell_size + cell_spacing)
                if row == selected_row and col == selected_col:
                    display.fill_rect(x, y, cell_size, cell_size, 1)  # Filled for selected cell
                else:
                    display.rect(x, y, cell_size, cell_size, 1)  # Outline for other cells
        HR = bytearray(heart_data)
        TEMP = bytearray(temp_data)
        Health = bytearray(health)
        fbHR = framebuf.FrameBuffer(HR, 16, 16, framebuf.MONO_HLSB)
        fbTEMP = framebuf.FrameBuffer(TEMP, 16, 20, framebuf.MONO_HLSB)
        fbHealth = framebuf.FrameBuffer(Health, 16, 16, framebuf.MONO_HLSB)
        display.blit(fbHR, 42,12)
        display.blit(fbTEMP, 75,8)
        display.blit(fbHealth, 42,41)
        display.show()
        break
    
    