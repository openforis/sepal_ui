from sepal_ui.scripts import utils as su
import string

def merge(input_files, out_filename=None, out_format=None, co=None, pixelsize=None, tap=False, separate=False, v=False, pct=False, extents=None, nodata_value=None, output_nodata_value=None, datatype=None, output=None):      
    """
    This utility will automatically mosaic a set of images. All the images must be in the same coordinate system and have a matching number of bands, but they may be overlapping, and at different resolutions. In areas of overlap, the last image will be copied over earlier ones.
    
    Args:
        input_files ([str]): The name of the input files
        out_filename (str, optional): The name of the output file, which will be created if it does not already exist (defaults to “out.tif”).
        out_format (str, optional): Select the output format. Starting with GDAL 2.3, if not specified, the format is guessed from the extension (previously was GTiff). Use the short format name.
        co (str, optional): Many formats have one or more optional creation options that can be used to control particulars about the file created. For instance, the GeoTIFF driver supports creation options to control compression, and whether the file should be tiled.

The creation options available vary by format driver, and some simple formats have no creation options at all. A list of options supported for a format can be listed with the –formats command line option but the documentation for the format is the definitive source of information on driver creation options. See Raster drivers format specific documentation for legal creation options for each format.
        pixelsize ([pixelsize_x, pixelsize_y], optional): Pixel size to be used for the output file. If not specified the resolution of the first input file will be used.
        tap (bool, optional): (target aligned pixels) align the coordinates of the extent of the output file to the values of the -tr, such that the aligned extent includes the minimum extent.
        separate (bool, optional): Place each input file into a separate band.
        v (bool, optional): Generate verbose output of mosaicing operations as they are done.
        pct (bool, optional): Grab a pseudo-color table from the first input image, and use it for the output. Merging pseudo-colored images this way assumes that all input files use the same color table.
        extents ([ulx, uly, lrx, lry], optional): The extents of the output file. If not specified the aggregate extents of all input files will be used
        nodata_value (int, optional): Ignore pixels from files being merged in with this pixel value.
        output_nodata_value(int, optional): Assign a specified nodata value to output bands.
        datatype(str, optional): Force the output image bands to have a specific data type supported by the driver, which may be one of the following: Byte, UInt16, Int16, UInt32, Int32, Float32, Float64, CInt16, CInt32, CFloat32 or CFloat64.
        output (v.alert, optional): the alert where to display the output
        
    Returns:
        process.stdout (str): complete output of the process
    """
    
    command = ['gdal_merge.py']
    
    if out_filename:
        command += ['-o', out_filename]
        
    if out_format:
        command += ['-of', out_format]
        
    if co:
        command += ['-co', co]
        
    if pixelsize:
        #check the integrity 
        if not isinstance(pixelsize, list):
            if output:
                output.add_live_msg('pixelsize is not an array ignoring option', 'error')
        else:
            command += ['-ps', str(pixelsize[0]), str(pixelsize[1])]
            
    if tap:
        command += ['-tap']
        
    if separate:
        command += ['-separate']
        
    if v:
        command += ['-v']
        
    if pct:
        command += ['-pct']
        
    if extents:
        #check the integrity 
        if not isinstance(extents, list):
            if output:
                output.add_msg('extents is not an array ignoring option', 'error')
        else:
            command += [
                '-ul_lr', 
                str(extents[0]), 
                str(extents[1]), 
                str(extents[2]), 
                str(extents[3])
            ]
    
    if nodata_value != None: #can be 0
        command += ['-n', str(nodata_value)]
        
    
    if output_nodata_value != None: #can be 0 
        command += ['-a_nodata', str(output_nodata_value)]
        
    if datatype:
        types = ['Byte', 'UInt16', 'Int16', 'UInt32', 'Int32', 'Float32', 'Float64', 'CInt16', 'CInt32', 'CFloat32', 'CFloat64']
        if not datatype in types:
            if output:
                outptu.add_msg('datatype not recognize ignoring option', 'error')
        else:
            command += ['-ot', datatype]
            
    command += input_files
    
    return su.launch(command, output)

def calc(expression, inputs, out_file, bands=None, no_data=None, type_=None, format_=None, co=None, overwrite=False, output=None):
    """
    Command line raster calculator with numpy syntax. Use any basic arithmetic supported by numpy arrays such as +, -, *, and \ along with logical operators such as >. Note that all files must have the same dimensions, but no projection checking is performed.
    
    Args:
        expression (str): Calculation in gdalnumeric syntax using +, -, /, *, or any numpy array functions (i.e. log10()).
        inputs ([raster]): Input gdal raster file, you can use any letter (A-Z).
        bands ([int], optionnal): Number of raster band for files. must be the same size as inputs with None value for defaults ex: [1,2,None,5]. Default value is one.
        output (str): Output file to generate or fill.
        no_data (int, optionnal): Output nodata value (default datatype specific value).
        type_ (str, optionnal): Output datatype, must be one of [Int32, Int16, Float64, UInt16, Byte, UInt32, Float32].
        format_ (str, optionnal): GDAL format for output file
        co (str, optionnal): Passes a creation option to the output format driver. Multiple options may be listed. See format specific documentation for legal creation options for each format.
        overwrite (bool): Overwrite output file if it already exists.
        output (v.alert, optional): the alert where to display the output
    """
    
    command = ['gdal_calc.py']
    
    command += ['--calc="{}"'.format(expression)]
    
    for i in range(min(len(inputs), 26)):
        command += ['-' + string.ascii_uppercase[i], inputs[i]]
        
    command += ['--outfile={}'.format(out_file)]
    
    if bands and len(bands) == len(inputs):
        for i in range(min(len(bands), 26)):
            command +=['-{0}_band={1}'.format(string.ascii_uppercase[i], bands[i])]
    
    if no_data:
        command += ['--NoDataValue={}'.format(no_data)]
    
    types = ['Int32', 'Int16', 'Float64', 'UInt16', 'Byte', 'UInt32', 'Float32']
    if type_ and (type_ in types):
        command += ['--type={}'.format(type_)]
    
    if format_:
        command += ['--format={}'.format(format_)]
        
    if co:
        command += ['--co={}'.format(co)]
        
    if overwrite == True:
        command += ['--overwrite']
        
    print(' '.join(command))
        
    return su.launch(command, output)
        
    