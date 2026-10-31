#!/usr/bin/env python3
"""Render the project-owned 1600x720 Levita 3D animation loops with Blender.

Run with Blender, for example:
  blender --background --python tools/render_levita_loops.py -- \
    --scene orbital-ring --output /tmp/orbital-ring --preview

The script renders PNG frames. Encoding stays a separate, explicit ffmpeg step so
interrupted renders can be resumed and the final H.264/yuv420p contract can be
verified independently.
"""

from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector


WIDTH = 1600
HEIGHT = 720
FPS = 20
SECONDS = 10
FRAMES = FPS * SECONDS
TAU = math.tau


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scene",
        required=True,
        choices=("orbital-ring", "neon-apex", "quantum-core"),
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--frame", type=int, default=73)
    parser.add_argument("--scale", type=int, choices=range(25, 101), default=100)
    parser.add_argument("--engine", choices=("eevee", "workbench"), default="eevee")
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def clear_scene() -> bpy.types.Scene:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = FRAMES
    scene.render.fps = FPS
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.compression = 35
    scene.render.use_file_extension = True
    scene.render.use_overwrite = True
    scene.render.use_placeholder = True
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGB"
    world = bpy.data.worlds.new("OHC Deep Space") if not scene.world else scene.world
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.001, 0.003, 0.012, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.11
    return scene


def material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    metallic: float = 0.0,
    roughness: float = 0.4,
    emission: tuple[float, float, float, float] | None = None,
    strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def assign(obj: bpy.types.Object, mat: bpy.types.Material) -> bpy.types.Object:
    obj.data.materials.append(mat)
    return obj


def parent_keep_transform(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def smooth(obj: bpy.types.Object) -> bpy.types.Object:
    if hasattr(obj.data, "polygons"):
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return obj


def bevel(obj: bpy.types.Object, width: float, segments: int = 4) -> bpy.types.Object:
    modifier = obj.modifiers.new("Soft machined edges", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    return obj


def cube(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    bevel_width: float = 0.08,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel(obj, bevel_width)
    return assign(obj, mat)


def sphere(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
    segments: int = 48,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=max(16, segments // 2), radius=radius, location=location
    )
    obj = bpy.context.object
    obj.name = name
    return assign(smooth(obj), mat)


def torus(
    name: str,
    location: tuple[float, float, float],
    major_radius: float,
    minor_radius: float,
    mat: bpy.types.Material,
    rotation: tuple[float, float, float] = (0, 0, 0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=96,
        minor_segments=16,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    return assign(smooth(obj), mat)


def cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    mat: bpy.types.Material,
    rotation: tuple[float, float, float] = (0, 0, 0),
    vertices: int = 48,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    bevel(obj, min(radius, depth) * 0.08)
    return assign(smooth(obj), mat)


def cone(
    name: str,
    location: tuple[float, float, float],
    radius1: float,
    radius2: float,
    depth: float,
    mat: bpy.types.Material,
    rotation: tuple[float, float, float] = (0, 0, 0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(
        vertices=48,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    return assign(smooth(obj), mat)


def empty(name: str, location=(0, 0, 0)) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    return obj


def camera_at(location, target, lens=50) -> bpy.types.Object:
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.name = "Levita widescreen camera"
    camera.data.lens = lens
    camera.data.sensor_width = 36
    point_at(camera, target)
    bpy.context.scene.camera = camera
    return camera


def point_at(obj: bpy.types.Object, target) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area_light(name, location, color, energy, size, target=(0, 0, 0)) -> None:
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.color = color
    light.data.shape = "DISK"
    light.data.size = size
    point_at(light, target)


def point_light(name, location, color, energy, radius=1.0) -> None:
    bpy.ops.object.light_add(type="POINT", location=location)
    light = bpy.context.object
    light.name = name
    light.data.color = color
    light.data.energy = energy
    light.data.shadow_soft_size = radius


def animate_turn(obj: bpy.types.Object, axis: int = 2, turns: float = 1.0) -> None:
    obj.rotation_mode = "XYZ"
    curve = obj.driver_add("rotation_euler", axis)
    curve.driver.expression = f"2*pi*{turns}*(frame-1)/{FRAMES}"


def animate_bob(obj: bpy.types.Object, amount: float = 0.15) -> None:
    start = obj.location.z
    curve = obj.driver_add("location", 2)
    curve.driver.expression = f"{start}+{amount}*sin(2*pi*(frame-1)/{FRAMES})"


def animate_pulse(obj: bpy.types.Object, amount: float = 0.07) -> None:
    for axis in range(3):
        base = obj.scale[axis]
        curve = obj.driver_add("scale", axis)
        curve.driver.expression = (
            f"{base}*(1+{amount}*sin(2*pi*(frame-1)/{FRAMES})"
            f"+{amount * 0.4}*sin(4*pi*(frame-1)/{FRAMES}))"
        )


def add_star_shell(seed: int, count: int = 90) -> None:
    rng = random.Random(seed)
    star_mat = material(
        "Cold stars",
        (0.6, 0.8, 1.0, 1),
        emission=(0.55, 0.75, 1.0, 1),
        strength=8,
    )
    warm_mat = material(
        "Warm stars",
        (1.0, 0.55, 0.25, 1),
        emission=(1.0, 0.4, 0.12, 1),
        strength=6,
    )
    for index in range(count):
        angle = rng.uniform(-1.25, 1.25)
        distance = rng.uniform(17, 28)
        x = math.sin(angle) * distance
        y = rng.uniform(4, 12)
        z = rng.uniform(-8, 10)
        size = rng.uniform(0.025, 0.09)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=size, location=(x, y, z))
        star = bpy.context.object
        star.name = f"Star {index:03d}"
        assign(star, warm_mat if index % 11 == 0 else star_mat)


def build_orbital_ring() -> None:
    scene = clear_scene()
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.002, 0.004, 0.018, 1)
    add_star_shell(811, 110)
    black = material("Obsidian alloy", (0.006, 0.012, 0.025, 1), metallic=0.92, roughness=0.2)
    blue = material("Ion blue", (0.01, 0.12, 0.6, 1), metallic=0.25, roughness=0.2, emission=(0.01, 0.22, 1.0, 1), strength=18)
    violet = material("Nebula violet", (0.3, 0.015, 0.8, 1), metallic=0.2, roughness=0.22, emission=(0.5, 0.02, 1.0, 1), strength=12)
    planet_mat = material("Ocean planet", (0.015, 0.08, 0.2, 1), metallic=0.05, roughness=0.72)
    atmosphere = material("Atmosphere", (0.02, 0.22, 0.8, 1), emission=(0.01, 0.18, 1.0, 1), strength=2.8, roughness=0.25)

    sphere("Distant ocean planet", (3.6, 5.7, -2.7), 4.2, planet_mat, 64)
    torus("Planet atmosphere rim", (3.6, 5.45, -2.7), 4.22, 0.035, atmosphere, (math.radians(90), 0, 0))
    ring_root = empty("Orbital gate root", (-1.1, 0.4, 0.25))
    outer = torus("Orbital gate hull", ring_root.location, 3.55, 0.23, black, (math.radians(90), 0, 0))
    inner = torus("Orbital gate plasma", ring_root.location, 3.2, 0.075, blue, (math.radians(90), 0, 0))
    accent = torus("Orbital gate violet rail", ring_root.location, 3.82, 0.045, violet, (math.radians(90), 0, 0))
    for obj in (outer, inner, accent):
        parent_keep_transform(obj, ring_root)
    for index in range(18):
        angle = TAU * index / 18
        x = ring_root.location.x + math.cos(angle) * 3.55
        z = ring_root.location.z + math.sin(angle) * 3.55
        block = cube(f"Gate segment {index:02d}", (x, 0.4, z), (0.16, 0.3, 0.42), blue if index % 3 == 0 else black, bevel_width=0.045)
        block.rotation_euler.y = -angle
        parent_keep_transform(block, ring_root)
    animate_turn(ring_root, axis=1, turns=1)

    orbit = empty("Asteroid orbit", ring_root.location)
    rng = random.Random(903)
    for index in range(20):
        angle = TAU * index / 20 + rng.uniform(-0.08, 0.08)
        radius = rng.uniform(4.6, 6.5)
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=rng.uniform(0.08, 0.32),
            location=(ring_root.location.x + math.cos(angle) * radius, rng.uniform(-0.2, 2.4), ring_root.location.z + math.sin(angle) * radius * 0.55),
        )
        rock = bpy.context.object
        rock.name = f"Orbital debris {index:02d}"
        rock.scale = (1.0, rng.uniform(0.45, 1.3), rng.uniform(0.6, 1.4))
        assign(rock, black)
        parent_keep_transform(rock, orbit)
    animate_turn(orbit, axis=1, turns=-0.5)

    ship = empty("Survey craft", (-5.0, -0.2, -1.0))
    body = cone("Survey craft body", ship.location, 0.5, 0.16, 2.4, black, (0, math.radians(90), 0))
    parent_keep_transform(body, ship)
    for side in (-1, 1):
        wing = cube("Survey craft wing", (-5.1, -0.2 + side * 0.78, -1.12), (0.62, 0.48, 0.07), black, bevel_width=0.04)
        wing.rotation_euler.z = math.radians(7 * side)
        parent_keep_transform(wing, ship)
        engine = sphere("Survey craft engine", (-5.58, -0.2 + side * 0.48, -1.02), 0.12, violet, 24)
        parent_keep_transform(engine, ship)
    animate_bob(ship, 0.23)
    animate_turn(ship, axis=0, turns=0.04)

    camera_at((0.0, -14.8, 3.6), (-0.7, 0.8, 0.0), lens=47)
    area_light("Planet key", (-4, -5, 8), (0.17, 0.36, 1.0), 1450, 7, (-1, 0, 0))
    point_light("Portal blue", (-1.1, -1.2, 0.3), (0.02, 0.22, 1.0), 850, 2.5)
    point_light("Portal violet", (-4.5, 0.0, 2.7), (0.5, 0.04, 1.0), 500, 1.8)


def build_neon_apex() -> None:
    scene = clear_scene()
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.003, 0.003, 0.009, 1)
    black = material("Gloss carbon", (0.008, 0.012, 0.02, 1), metallic=0.95, roughness=0.14)
    body_mat = material("Midnight blue body", (0.008, 0.04, 0.16, 1), metallic=0.88, roughness=0.17)
    tire_mat = material("Tyre rubber", (0.004, 0.004, 0.006, 1), roughness=0.82)
    glass = material("Electric glass", (0.005, 0.08, 0.18, 1), metallic=0.35, roughness=0.08, emission=(0.0, 0.11, 0.3, 1), strength=1.8)
    cyan = material("Apex cyan", (0.0, 0.25, 0.8, 1), emission=(0.0, 0.5, 1.0, 1), strength=21)
    magenta = material("Apex magenta", (0.8, 0.01, 0.35, 1), emission=(1.0, 0.01, 0.22, 1), strength=15)
    floor_mat = material("Wet graphite", (0.006, 0.009, 0.016, 1), metallic=0.75, roughness=0.22)

    cube("Ground", (0, 0, -0.18), (16, 16, 0.18), floor_mat, bevel_width=0)
    for index in range(-10, 11):
        grid_x = cube(f"Grid X {index}", (index * 1.35, 0, 0.018), (0.012, 15, 0.008), cyan if index % 5 == 0 else magenta, bevel_width=0)
        grid_x.data.materials[0] = cyan if index % 5 == 0 else magenta
    for index in range(-10, 11):
        cube(f"Grid Y {index}", (0, index * 1.35, 0.02), (15, 0.012, 0.008), cyan if index % 4 else magenta, bevel_width=0)

    root = empty("Neon Apex turntable", (-1.0, 0, 0))
    chassis = cube("Apex lower chassis", (-1.0, 0, 0.76), (3.2, 1.35, 0.38), body_mat, bevel_width=0.32)
    nose = cube("Apex nose", (-3.25, 0, 0.82), (1.2, 1.28, 0.24), body_mat, bevel_width=0.28)
    nose.rotation_euler.y = math.radians(-5)
    rear = cube("Apex rear deck", (1.55, 0, 1.0), (0.85, 1.25, 0.28), black, bevel_width=0.22)
    cabin = cube("Apex canopy", (-0.2, 0, 1.47), (1.35, 1.04, 0.5), glass, bevel_width=0.48)
    roof = cube("Apex roof spine", (0.0, 0, 1.92), (0.78, 0.78, 0.09), black, bevel_width=0.08)
    for obj in (chassis, nose, rear, cabin, roof):
        parent_keep_transform(obj, root)
    for side in (-1, 1):
        rail = cube("Apex side light", (-1.0, side * 1.37, 0.63), (2.65, 0.035, 0.055), cyan, bevel_width=0.02)
        parent_keep_transform(rail, root)
        tail = cube("Apex tail light", (1.86, side * 0.66, 1.13), (0.05, 0.48, 0.08), magenta, bevel_width=0.025)
        parent_keep_transform(tail, root)
    front_light = cube("Apex front light", (-4.32, 0, 0.93), (0.045, 0.92, 0.08), cyan, bevel_width=0.02)
    parent_keep_transform(front_light, root)

    for x in (-2.55, 1.35):
        for y in (-1.34, 1.34):
            wheel = cylinder("Apex wheel", (x, y, 0.64), 0.68, 0.44, tire_mat, (math.radians(90), 0, 0), 64)
            parent_keep_transform(wheel, root)
            rim = cylinder("Apex luminous rim", (x, y * 1.012, 0.64), 0.42, 0.47, cyan if x < 0 else magenta, (math.radians(90), 0, 0), 64)
            parent_keep_transform(rim, root)
            hub = cylinder("Apex hub", (x, y * 1.018, 0.64), 0.18, 0.49, black, (math.radians(90), 0, 0), 48)
            parent_keep_transform(hub, root)

    spoiler = cube("Apex spoiler", (2.05, 0, 1.76), (0.12, 1.55, 0.08), black, bevel_width=0.05)
    parent_keep_transform(spoiler, root)
    for side in (-1, 1):
        stand = cube("Apex spoiler stand", (1.75, side * 0.8, 1.46), (0.08, 0.08, 0.35), black, bevel_width=0.03)
        parent_keep_transform(stand, root)
    animate_turn(root, axis=2, turns=1)
    animate_bob(root, 0.06)

    for radius, z, mat in ((6.2, 2.7, cyan), (7.4, 3.2, magenta), (8.7, 3.7, cyan)):
        torus("Apex tunnel hoop", (0, 4.5, z), radius, 0.045, mat, (math.radians(90), 0, 0))
    camera_at((7.8, -12.2, 5.0), (-1.0, 0.2, 0.85), lens=53)
    area_light("Apex cool key", (-4, -5, 8), (0.12, 0.35, 1.0), 1800, 6, (-1, 0, 0.8))
    area_light("Apex pink rim", (5, 4, 4), (1.0, 0.02, 0.24), 1300, 5, (0, 0, 1))
    point_light("Apex underglow", (-1, 0, 0.35), (0.0, 0.35, 1.0), 900, 2.2)


def build_quantum_core() -> None:
    scene = clear_scene()
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.002, 0.002, 0.012, 1)
    add_star_shell(4242, 70)
    metal = material("Reactor gunmetal", (0.008, 0.015, 0.028, 1), metallic=0.96, roughness=0.19)
    white = material("Reactor ceramic", (0.35, 0.48, 0.62, 1), metallic=0.55, roughness=0.25)
    cyan = material("Quantum cyan", (0.0, 0.3, 0.75, 1), emission=(0.0, 0.55, 1.0, 1), strength=23)
    violet = material("Quantum violet", (0.42, 0.01, 0.75, 1), emission=(0.55, 0.015, 1.0, 1), strength=18)
    core_mat = material("Living core", (0.01, 0.15, 0.8, 1), metallic=0.15, roughness=0.08, emission=(0.02, 0.45, 1.0, 1), strength=25)
    floor_mat = material("Reactor floor", (0.004, 0.007, 0.015, 1), metallic=0.75, roughness=0.28)
    cube("Reactor chamber floor", (0, 0, -2.55), (15, 15, 0.18), floor_mat, bevel_width=0)
    for radius in (2.3, 4.1, 6.2):
        torus("Floor energy ring", (-1.0, 0, -2.34), radius, 0.035, cyan if radius != 4.1 else violet)

    root = empty("Quantum core root", (-1.0, 0.4, 0.4))
    core = sphere("Quantum energy core", root.location, 1.45, core_mat, 64)
    parent_keep_transform(core, root)
    animate_turn(core, axis=2, turns=1)
    animate_bob(core, 0.12)
    animate_pulse(core)
    bsdf = core_mat.node_tree.nodes.get("Principled BSDF")
    strength = bsdf.inputs["Emission Strength"]
    pulse = strength.driver_add("default_value")
    pulse.driver.expression = f"27+8*sin(2*pi*(frame-1)/{FRAMES})+4*sin(4*pi*(frame-1)/{FRAMES})"

    ring_a = torus("Quantum ring A", root.location, 2.45, 0.14, metal, (math.radians(70), math.radians(8), 0))
    ring_b = torus("Quantum ring B", root.location, 2.85, 0.07, cyan, (math.radians(20), math.radians(65), 0))
    ring_c = torus("Quantum ring C", root.location, 3.25, 0.095, violet, (math.radians(105), math.radians(25), 0))
    for obj in (ring_a, ring_b, ring_c):
        parent_keep_transform(obj, root)
    animate_turn(ring_a, axis=2, turns=1)
    animate_turn(ring_b, axis=0, turns=-1)
    animate_turn(ring_c, axis=1, turns=0.5)

    satellites = empty("Reactor satellites", root.location)
    for index in range(8):
        angle = TAU * index / 8
        radius = 4.05
        x = root.location.x + math.cos(angle) * radius
        z = root.location.z + math.sin(angle) * radius * 0.65
        pod = cube(f"Reactor satellite {index}", (x, 0.4 + math.sin(angle * 2) * 0.5, z), (0.22, 0.45, 0.62), white if index % 2 else metal, bevel_width=0.12)
        pod.rotation_euler.y = -angle
        parent_keep_transform(pod, satellites)
        slit = cube(f"Satellite light {index}", (x, 0.0 + math.sin(angle * 2) * 0.5, z), (0.08, 0.025, 0.36), cyan if index % 2 else violet, bevel_width=0.02)
        parent_keep_transform(slit, satellites)
    animate_turn(satellites, axis=1, turns=-1)

    for x in (-7.2, 5.2):
        column = cylinder("Reactor tower", (x, 3.2, 0.2), 0.7, 6.3, metal, vertices=64)
        column.rotation_euler.x = 0
        torus("Tower light", (x, 3.2, 0.8), 0.73, 0.055, violet if x < 0 else cyan)
        torus("Tower light", (x, 3.2, -0.9), 0.73, 0.055, cyan if x < 0 else violet)
    camera_at((0.0, -15.8, 4.0), (-1.0, 0.6, 0.2), lens=49)
    area_light("Reactor top key", (-1, -3, 9), (0.16, 0.34, 1.0), 1700, 7, (-1, 0, 0))
    point_light("Core cyan spill", (-1, -1, 0.4), (0.0, 0.38, 1.0), 1250, 2.8)
    point_light("Core violet spill", (-4.8, 1.0, 2.4), (0.55, 0.02, 1.0), 850, 2.0)


BUILDERS = {
    "orbital-ring": build_orbital_ring,
    "neon-apex": build_neon_apex,
    "quantum-core": build_quantum_core,
}


def main() -> None:
    args = parse_args()
    BUILDERS[args.scene]()
    scene = bpy.context.scene
    if args.engine == "workbench":
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "MATERIAL"
        scene.display.shading.background_type = "VIEWPORT"
        scene.display.shading.background_color = (0.0015, 0.002, 0.008)
        scene.display.shading.show_shadows = True
        scene.display.shading.show_cavity = True
        scene.display.shading.cavity_type = "WORLD"
        scene.display.shading.show_specular_highlight = True
    scene.render.resolution_percentage = args.scale
    if args.preview:
        scene.render.image_settings.color_mode = "RGB"
        scene.render.filepath = str(args.output.with_suffix(".png"))
        scene.frame_set(max(1, min(FRAMES, args.frame)))
        bpy.ops.render.render(write_still=True)
    else:
        args.output.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(args.output / f"{args.scene}-")
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
