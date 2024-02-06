![EPFL Center for Imaging logo](https://imaging.epfl.ch/resources/logo-for-gitlab.svg)
# napari-rembg

Select the foreground of images using AI in Napari. This plugin is based on the [rembg](https://github.com/danielgatis/rembg) project.

<p align="center">
    <img src="https://github.com/EPFL-Center-for-Imaging/napari-rembg/blob/main/assets/demo.gif" height="400">
</p>

### Why use `napari-rembg`?
- It runs **fast** even on a laptop's CPU (a few seconds per image).
- It is **easy to install** compared to other AI tools for segmentation.
- It is a **quick and easy** solution to automatically extract the foreground of scientific and natural images.

This plugin is primarily intended for analyzing **2D** and **2D (RGB)** images, however it can also be used to segment a particular slice in a **2D + time**, **2D + channel** or **3D** image.

## New!

Run `rembg` in individual regions of interest defined by bounding boxes to segment multiple objects:

<p align="center">
    <img src="https://github.com/EPFL-Center-for-Imaging/napari-rembg/blob/main/assets/screenshot.gif" height="400">
</p>

- Insert a `Shapes` layer and **draw rectangles** to define regions of interest (ROIs) in which to run the foreground selection. You can choose to auto-increment the label index to distinguish objects in different ROIs.
- Select the `Labels` layer in which to write the output of the foreground segmentation (or let the plugin create a `Labels` layer automatically).

## Installation

You can install `napari-rembg` via [pip]:

    pip install napari-rembg

## Usage

Start `napari-rembg` from the `Plugins` menu of Napari:

```
Plugins > Select foreground (napari-rembg)
```

## Contributing

Contributions are very welcome. 

## License

Distributed under the terms of the [BSD-3] license,
"napari-rembg" is free and open source software.

## Issues

If you encounter any problems, please file an issue along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.
