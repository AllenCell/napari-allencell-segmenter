A plugin that enables 3D image segmentation provided by Allen Institute for Cell Science

The Allen Cell & Structure Segmenter plugin for napari provides an intuitive graphical user interface to access the powerful segmentation capabilities of an open source 3D segmentation software package developed and maintained by the Allen Institute for Cell Science (classic workflows only with v1.0). ​The Allen Cell & Structure Segmenter is a Python-based open source toolkit developed at the Allen Institute for Cell Science for 3D segmentation of intracellular structures in fluorescence microscope images. This toolkit brings together classic image segmentation and iterative deep learning workflows first to generate initial high-quality 3D intracellular structure segmentations and then to easily curate these results to generate the ground truths for building robust and accurate deep learning models. The toolkit takes advantage of the high replicate 3D live cell image data collected at the Allen Institute for Cell Science of over 30 endogenous fluorescently tagged human induced pluripotent stem cell (hiPSC) lines. Each cell line represents a different intracellular structure with one or more distinct localization patterns within undifferentiated hiPS cells and hiPSC-derived cardiomyocytes.

## Installation

### Option 1 (recommended):

After you installed the lastest version of napari, you can go to "Plugins" --> "Install/Uninstall Package(s)". Then, you will be able to see all available napari plugins and you can find us by name `napari-allencell-segmenter`. Just click the "install" button to install the Segmenter plugin.

### Option 2:

You can also install `napari-allencell-segmenter` via [pip]:

    pip install napari-allencell-segmenter

## Quick Start

In the current version, there are two parts in the plugin: **workflow editor** and **batch processing**. The **workflow editor** allows users adjusting parameters in all the existing workflows in the lookup table, so that the workflow can be optimized on users' data. The adjusted workflow can be saved and then applied to a large batch of files using the **batch processing** part of the plugin. 

1. Open a file in napari (the plugin is able to support multi-dimensional data in .tiff, .tif. ome.tif, .ome.tiff, .czi)
2. Start the plugin (open napari, go to "Plugins" --> "Add Dock Widget" --> "napari-allencell-segmenter" --> "workflow editor")
3. Select the image and channel to work on
4. Select a workflow based on the example image and target segmentation based on user's data. Ideally, it is recommend to start with the example with very similar morphology as user's data.
5. Click "Run All" to execute the whole workflow on the sample data.
6. Adjust the parameters of steps, based on the intermediate results. For instruction on the details on each function and the effect of each parameter, click the tooltip button. A complete list of all functions can be found [here](https://github.com/AllenCell/aics-segmentation/blob/main/aicssegmentation/structure_wrapper_config/function_params.md)
7. Click "Run All" again after adjusting the parameters and repeat step 6 and 7 until the result is satisfactory.
8. Save the workflow
9. Close the plugin and open the **batch processing** part by (go to "Plugins" --> "Add Dock Widget" --> "napari-allencell-segmenter" --> "batch processing")
10. Load the customized workflow (or an off-the-shelf workflow) json file
11. Load the folder with all the images to process
12. Click "Run"