import os
import math
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ==================================================
# CONFIG
# ==================================================

GCODE_FILE = "test.gcode"

OUTPUT_DIR = "outputs/renders"


# Render this layer
TARGET_LAYER = 300


# Virtual camera
#
# Distance does not affect orthographic scale,
# but controls camera placement.
#
CAMERA_DISTANCE = 800


# Rotation around print center
#
# X = pitch
# Y = roll
# Z = yaw
#
CAMERA_PITCH = 0
CAMERA_ROLL = 0
CAMERA_YAW = 0


# Image settings

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

DPI = 600


LINE_WIDTH = 1.0

# Background color
BACKGROUND_COLOR = "white"

# Extrusion line color
LINE_COLOR = "#152885"

# Alternative examples:
# LINE_COLOR = "#404040"
# LINE_COLOR = "#00FF00"
# LINE_COLOR = (0.2, 0.2, 0.2)


# ==================================================
# GCODE PARSER
# ==================================================

def parse_gcode(filename):

    layers = {}

    x = 0
    y = 0
    z = 0
    e = 0

    current_layer = 0


    print("Parsing G-code...")


    with open(
        filename,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:


        for line in file:

            line = line.strip()


            if not line:
                continue


            # layer marker

            if line.startswith(";LAYER:"):

                try:

                    current_layer = int(
                        line.split(":")[1]
                    )

                    layers.setdefault(
                        current_layer,
                        []
                    )

                except:

                    pass


                continue



            if not line.startswith(
                ("G0", "G1")
            ):
                continue



            new_x = x
            new_y = y
            new_z = z
            new_e = e



            for value in line.split():

                axis = value[:1]
                number = value[1:]

                if not number:
                    continue

                try:
                    number = float(number)
                except ValueError:
                    print(f"Skipping token '{value}'")
                    continue

                if axis == "X":
                    new_x = number
                elif axis == "Y":
                    new_y = number
                elif axis == "Z":
                    new_z = number
                elif axis == "E":
                    new_e = number



            # extrusion movement

            if new_e > e:


                if (
                    new_x != x or
                    new_y != y or
                    new_z != z
                ):

                    layers.setdefault(
                        current_layer,
                        []
                    ).append(
                        (
                            x,
                            y,
                            z,
                            new_x,
                            new_y,
                            new_z
                        )
                    )



            x = new_x
            y = new_y
            z = new_z
            e = new_e



    print(
        f"Loaded {len(layers)} layers"
    )


    return layers



# ==================================================
# GEOMETRY
# ==================================================

def get_bounds(layers):

    points = []


    for segments in layers.values():

        for s in segments:

            points.append(
                (s[0],s[1],s[2])
            )

            points.append(
                (s[3],s[4],s[5])
            )



    points=np.array(points)


    minimum = points.min(axis=0)
    maximum = points.max(axis=0)


    center = (
        minimum +
        maximum
    ) / 2



    return minimum, maximum, center



# ==================================================
# CAMERA
# ==================================================

def rotation_matrix():

    pitch = math.radians(
        CAMERA_PITCH
    )

    roll = math.radians(
        CAMERA_ROLL
    )

    yaw = math.radians(
        CAMERA_YAW
    )



    Rx = np.array(
        [
            [1,0,0],
            [0,math.cos(pitch),-math.sin(pitch)],
            [0,math.sin(pitch),math.cos(pitch)]
        ]
    )



    Ry = np.array(
        [
            [math.cos(roll),0,math.sin(roll)],
            [0,1,0],
            [-math.sin(roll),0,math.cos(roll)]
        ]
    )



    Rz = np.array(
        [
            [math.cos(yaw),-math.sin(yaw),0],
            [math.sin(yaw),math.cos(yaw),0],
            [0,0,1]
        ]
    )


    return Rz @ Ry @ Rx



def project_points(points, center):


    # move origin to print center

    points = points - center


    R = rotation_matrix()


    rotated = (
        R @ points.T
    ).T



    # orthographic projection

    projected = rotated[
        :,
        [
            0,
            2
        ]
    ]


    return projected



# ==================================================
# RENDER
# ==================================================

def render(
    layers,
    target_layer
):


    minimum, maximum, center = (
        get_bounds(layers)
    )



    projected_segments=[]



    for layer, segments in layers.items():

        if layer > target_layer:
            break


        for s in segments:


            points=np.array(
                [
                    [
                        s[0],
                        s[1],
                        s[2]
                    ],

                    [
                        s[3],
                        s[4],
                        s[5]
                    ]
                ]
            )



            p = project_points(
                points,
                center
            )



            projected_segments.append(
                p
            )



    print(
        f"Rendering {len(projected_segments)} paths"
    )



    fig = plt.figure(
        figsize=(
            IMAGE_WIDTH / DPI,
            IMAGE_HEIGHT / DPI
        ),
        facecolor=BACKGROUND_COLOR
    )


    ax = fig.add_axes(
        [
            0,
            0,
            1,
            1
        ]
    )

    ax.set_facecolor(BACKGROUND_COLOR)
    
    ax.axis(
        "off"
    )



    for segment in projected_segments:

        ax.plot(
            segment[:,0],
            segment[:,1],
            linewidth=LINE_WIDTH,
            color=LINE_COLOR,
            solid_capstyle="round"
        )



    ax.set_aspect(
        "equal"
    )



    all_points=np.vstack(
        projected_segments
    )


    padding = (
        all_points.max()
        -
        all_points.min()
    ) * 0.1



    ax.set_xlim(
        all_points[:,0].min()-padding,
        all_points[:,0].max()+padding
    )


    ax.set_ylim(
        all_points[:,1].min()-padding,
        all_points[:,1].max()+padding
    )



    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )



    output=os.path.join(
        OUTPUT_DIR,
        f"layer_{target_layer}.png"
    )


    plt.savefig(
        output,
        dpi=DPI,
        bbox_inches="tight",
        pad_inches=0
    )


    plt.close(
        fig
    )


    print(
        "Saved:",
        output
    )



# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":


    layers = parse_gcode(
        GCODE_FILE
    )


    render(
        layers,
        TARGET_LAYER
    )