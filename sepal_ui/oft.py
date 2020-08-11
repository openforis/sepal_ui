from sepal_ui.scripts import utils as su

def clump(inputfile, outputfile, band=None, maskfile=None, output=None):
    """ clump the results
    
    Args:
        inputfile (str): pathname to input file
        clump_map (str): pathname to the output file
        band (str, optional): Use image BAND number band
        maskfile (str, optional): use mask file and process only areas having mask value > 0
        output (v.alert, optional): the alert where to display the output
    
    Returns:
        process.stdout (str): complete output of the process
    """
    command = [
        'oft-clump',
        '-i', inputfile,
        '-o', outputfile,
    ]
    if band: 
        command += ['-b', band]
    if maskfile: 
        command += ['-um', maskfile] 

    return su.launch(command, output)

def his(infile, outfile, maskfile=None, hr=False, compact=False, maxval=None, output=None):
    """computes image histogram by segments
    
    Args:
        infile (str): specify input image file
        outfile (str): specify output text file
        maskfile (str, optional): specify mask file
        hr (bool, optional): use human readable output format
        compact (bool, optional): use compact output format
        maxval (int, optional): give maximum input value
        output (v.alert, optional): the alert where to display the output
        
    Results:
        process.stdout (str): complete output of the process
    """
    
    command = [
        'oft-his',
        '-i', infile,
        '-o', outfile
    ]
    if maskfile:
        command += ['-um', maskfile]
    if hr:
        command += ['-hr']
    if compact:
        command += ['-compact']
    if maxval:
        command += ['-maxval', str(maxval)]
    
    return su.launch(command, output)


        