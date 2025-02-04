# -*- encoding:utf-8 -*-
# ~ http://www.awaresystems.be/imaging/tiff.html
# ~ https://www.exiv2.org/tags.html

from Tyf import reduce

"""
Tags are defined as:

  <tag number>: ("tag name", [<tag type>], "tag description")

For tag number/name/description see for example:

  https://exiv2.org/tags.html

Note that <tag type> is _NOT_ exif-type, but the mapping defined in
__init__.py.TYPES. e.g. a byte or unsigned short is 1 even though
exif defines BYTE as 1 and SHORT as 3
"""

# Baseline TIFF tags
bTT = {
    254:   ("NewSubfileType", [1], (0,), "A general indication of the kind of data contained in this subfile"),
    255:   ("SubfileType", [1], None, "Deprecated, use NewSubfiletype instead"),
    256:   ("ImageWidth", [1,4], None, "Number of columns in the image, ie, the number of pixels per row"),
    257:   ("ImageLength", [1,4], None, "Number of rows of pixels in the image"),
    258:   ("BitsPerSample", [1], (1,), "Array size = SamplesPerPixel, number of bits per component"),
    259:   ("Compression", [1], (1,), "Compression scheme used on the image data"),
    262:   ("PhotometricInterpretation", [1], None, "The color space of the image data"),
    263:   ("Thresholding", [1], (1,), "For black and white TIFF files that represent shades of gray, the technique used to convert from gray to black and white pixels"),
    264:   ("CellWidth", [1], None, "The width of the dithering or halftoning matrix used to create a dithered or halftoned bilevel file"),
    265:   ("CellLength", [1], None, "The length of the dithering or halftoning matrix used to create a dithered or halftoned bilevel file"),
    266:   ("FillOrder", [1], (1,), "The logical order of bits within a byt"),
    270:   ("ImageDescription", [2], None, "A string that describes the subject of the image"),
    271:   ("Make", [2], None, "The scanner manufacturer"),
    272:   ("Model", [2], None, "The scanner model name or number"),
    273:   ("StripOffsets", [1,4], None, "For each strip, the byte offset of that strip"),
    274:   ("Orientation", [1], (1,), "The orientation of the image with respect to the rows and columns"),
    277:   ("SamplesPerPixel", [1], (1,), "The number of components per pixel"),
    278:   ("RowsPerStrip", [1,4], (2**32-1,), "The number of rows per strip"),
    279:   ("StripByteCounts", [1,4], None, "For each strip, the number of bytes in the strip after compression"),
    280:   ("MinSampleValue", [1], (0,), "The minimum component value used"),
    281:   ("MaxSampleValue", [1], (1,), "The maximum component value used"),
    282:   ("XResolution", [5], None, "The number of pixels per ResolutionUnit in the ImageWidth direction"),
    283:   ("YResolution", [5], None, "The number of pixels per ResolutionUnit in the ImageLength direction"),
    284:   ("PlanarConfiguration", [1], (1,), "How the components of each pixel are stored"),
    288:   ("FreeOffsets", [4], None, "For each string of contiguous unused bytes in a TIFF file, the byte offset of the string"),
    289:   ("FreeByteCounts", [4], None, "For each string of contiguous unused bytes in a TIFF file, the number of bytes in the string"),
    290:   ("GrayResponseUnit", [1], (2,), "The precision of the information contained in the GrayResponseCurve"),
    291:   ("GrayResponseCurve", [1], (2,), "Array size = 2**SamplesPerPixel"),
    296:   ("ResolutionUnit", [4], (2,), "The unit of measurement for XResolution and YResolution"),
    305:   ("Software", [2], None, "Name and version number of the software package(s) used to create the image"),
    306:   ("DateTime", [2], None, "Date and time of image creation, aray size = 20, 'YYYY:MM:DD HH:MM:SS\0'"),
    315:   ("Artist", [2], None, "Person who created the image"),
    316:   ("HostComputer", [2], None, "The computer and/or operating system in use at the time of image creation"),
    320:   ("ColorMap", [1], None, "A color map for palette color images"),
    338:   ("ExtraSamples", [1], (1,), "Description of extra components"),
    33432: ("Copyright", [2], None, "Copyright notice"),
}

# Extension TIFF tags
xTT = {
    269:   ("DocumentName", [2], None, "The name of the document from which this image was scanned"),
    285:   ("PageName", [2], None, "The name of the page from which this image was scanned"),
    286:   ("XPosition", [5], None, "X position of the image"),
    287:   ("YPosition", [5], None, "Y position of the image"),
    292:   ("T4Options", [4], (0,), "Options for Group 3 Fax compression"),
    293:   ("T6Options", [4], (0,), "Options for Group 6 Fax compression"),
    297:   ("PageNumber", [1], None, "The page number of the page from which this image was scanned"),
    301:   ("TransferFunction", [1], (1*(1<<1),), "Describes a transfer function for the image in tabular style"),
    317:   ("Predictor", [3], (1,), "A mathematical operator that is applied to the image data before an encoding scheme is applied"),
    318:   ("WhitePoint", [5], None, "The chromaticity of the white point of the image"),
    319:   ("PrimaryChromaticies", [5], None, "The chromaticities of the primaries of the image"),
    321:   ("HalftoneHints", [1], None, "Conveys to the halftone function the range of gray levels within a colorimetrically-specified image that should retain tonal detail"),
    322:   ("TileWidth", [1,4], None, "The tile width in pixels This is the number of columns in each tile"),
    323:   ("TileLength", [1,4], None, "The tile length (height) in pixels This is the number of rows in each tile"),
    324:   ("TileOffsets", [4], None, "For each tile, the byte offset of that tile, as compressed and stored on disk"),
    325:   ("TileByteCounts", [1,4], None, "For each tile, the number of (compressed) bytes in that tile"),
    326:   ("BadFaxLinea", [1,4], None, "Used in the TIFF-F standard, denotes the number of 'bad' scan lines encountered by the facsimile device"),
    327:   ("CleanFaxData", [1], None, "Used in the TIFF-F standard, indicates if 'bad' lines encountered during reception are stored in the data, or if 'bad' lines have been replaced by the receiver"),
    328:   ("ConsecutiveBadFaxLines", [1,4], None, "Used in the TIFF-F standard, denotes the maximum number of consecutive 'bad' scanlines received"),
    330:   ("SubIFDs", [2,4], None, "Offset to child IFDs"), # ???
    332:   ("InkSet", [1], None, "The set of inks used in a separated (PhotometricInterpretation=5) image"),
    333:   ("InkNames", [2], None, "The name of each ink used in a separated image"),
    334:   ("NumberOfInks", [1], (4,), "The number of inks"),
    336:   ("DotRange", [1,3], (0,1), "The component values that correspond to a 0%% dot and 100%% dot"),
    337:   ("TargetPrinter", [2], None, "A description of the printing environment for which this separation is intended"),
    339:   ("SampleFormat", [1], (1,), "Specifies how to interpret each data sample in a pixel"),
    340:   ("SMinSampleValue", [3,7,8,12], None, "Specifies the minimum sample value"),
    341:   ("SMaxSampleValue", [3,7,8,12], None, "Specifies the maximum sample value"),
    342:   ("TransferRange", [1], None, "Expands the range of the TransferFunction"),
    343:   ("ClipPath", [3], None, "Mirrors the essentials of PostScript's path creation functionality"),
    344:   ("XClipPathUnits", [4], None, "The number of units that span the width of the image, in terms of integer ClipPath coordinates"),
    345:   ("YClipPathUnits", [4], None, "The number of units that span the height of the image, in terms of integer ClipPath coordinates"),
    346:   ("Indexed", [1], (0,), "Aims to broaden the support for indexed images to include support for any color space"),
    347:   ("JPEGTables", [7], None, "JPEG quantization and/or Huffman tables"),
    351:   ("OPIProxy", [1], (0,), "OPI-related"),
    400:   ("GlobalParametersIFD", [2,4], None, "Used in the TIFF-FX standard to point to an IFD containing tags that are globally applicable to the complete TIFF file"),
    401:   ("ProfileType", [4], None, "Used in the TIFF-FX standard, denotes the type of data stored in this file or IFD"),
    402:   ("FaxProfile", [3], None, "Used in the TIFF-FX standard, denotes the 'profile' that applies to this file"),
    403:   ("CodingMethods", [4], None, "Used in the TIFF-FX standard, indicates which coding methods are used in the file"),
    404:   ("VersionYear", [3], None, "Used in the TIFF-FX standard, denotes the year of the standard specified by the FaxProfile field"),
    405:   ("ModeNumber", [3], None, "Used in the TIFF-FX standard, denotes the mode of the standard specified by the FaxProfile field"),
    433:   ("Decode", [10],None, "Used in the TIFF-F and TIFF-FX standards, holds information about the ITULAB (PhotometricInterpretation = 10) encoding"),
    434:   ("DefaultImageColor", [1], None, "Defined in the Mixed Raster Content part of RFC 2301, is the default color needed in areas where no image is available"),
    512:   ("JPEGProc", [1], None, "Old-style JPEG compression field TechNote2 invalidates this part of the specification"),
    513:   ("JPEGInterchangeFormat", [4], None, "Old-style JPEG compression field TechNote2 invalidates this part of the specification"),
    514:   ("JPEGInterchangeFormatLength", [4], None, "Old-style JPEG compression field TechNote2 invalidates this part of the specification"),
    515:   ("JPEGRestartInterval", [1], None, "Old-style JPEG compression field TechNote2 invalidates this part of the specification"),
    517:   ("JPEGLosslessPredictors", [1], None, "Old-style JPEG compression field TechNote2 invalidates this part of the specification"),
    518:   ("JPEGPointTransforms", [1], None, "Old-style JPEG compression field TechNote2 invalidates this part of the specification"),
    519:   ("JPEGQTables", [4], None, "Old-style JPEG compression field TechNote2 invalidates this part of the specification"),
    520:   ("JPEGDCTables", [4], None, "Old-style JPEG compression field TechNote2 invalidates this part of the specificationl"),
    521:   ("JPEGACTables", [4], None, "Old-style JPEG compression field TechNote2 invalidates this part of the specification"),
    529:   ("YCbCrCoefficients", [5], (299,1000,587,1000,114,1000), "The transformation from RGB to YCbCr image data"),
    530:   ("YCbCrSubSampling", [1], (2,2), "Specifies the subsampling factors used for the chrominance components of a YCbCr image"),
    531:   ("YCbCrPositioning", [1], (1,), "Specifies the positioning of subsampled chrominance components relative to luminance samples"),
    532:   ("ReferenceBlackWhite", [5], (0,1,1,1,0,1,1,1,0,1,1,1), "Specifies a pair of headroom and footroom image data values (codes) for each pixel component"),
    559:   ("StripRowCounts", [4], None, "Defined in the Mixed Raster Content part of RFC 2301, used to replace RowsPerStrip for IFDs with variable-sized strips"),
    700:   ("XMP", [3], None, "XML packet containing XMP metadata"),
    32781: ("ImageID", [2], None, "OPI-related"),
    34732: ("ImageLayer", [1,4], None, "Defined in the Mixed Raster Content part of RFC 2301, used to denote the particular function of this Image in the mixed raster scheme"),
}

# Private TIFF tags
pTT = {
    32932:  ("Wang Annotation", [3], None, "Annotation data, as used in 'Imaging for Windows'"),
    33445:  ("MD FileTag", [4], None, "Specifies the pixel data format encoding in the Molecular Dynamics GEL file format"),
    33446:  ("MD ScalePixel", [5], None, "Specifies a scale factor in the Molecular Dynamics GEL file format"),
    33447:  ("MD ColorTable", [1], None, "Used to specify the conversion from 16bit to 8bit in the Molecular Dynamics GEL file format"),
    33448:  ("MD LabName", [2], None, "Name of the lab that scanned this file, as used in the Molecular Dynamics GEL file format"),
    33449:  ("MD SampleInfo", [2], None, "Information about the sample, as used in the Molecular Dynamics GEL file format"),
    33450:  ("MD PrepDate", [2], None, "Date the sample was prepared, as used in the Molecular Dynamics GEL file format"),
    33451:  ("MD PrepTime", [2], None, "Time the sample was prepared, as used in the Molecular Dynamics GEL file format"),
    33452:  ("MD FileUnits", [2], None, "Units for data in this file, as used in the Molecular Dynamics GEL file format"),
    33550:  ("ModelPixelScaleTag", [12], None, "Used in interchangeable GeoTIFF files"),
    33723:  ("IPTC", [3,7], None, "IPTC (International Press Telecommunications Council) metadata"),
    33918:  ("INGR Packet Data Tag", [3], None, "Intergraph Application specific storage"),
    33919:  ("INGR Flag Registers", [4], None, "Intergraph Application specific flags"),
    33920:  ("IrasB Transformation Matrix", [12], None, "Originally part of Intergraph's GeoTIFF tags, but likely understood by IrasB only"),
    33922:  ("ModelTiepointTag", [12], None, "Originally part of Intergraph's GeoTIFF tags, but now used in interchangeable GeoTIFF files"),
    34264:  ("ModelTransformationTag", [12], None, "Used in interchangeable GeoTIFF files"),
    34377:  ("Photoshop", [1], None, "Collection of Photoshop 'Image Resource Blocks'"),
    34665:  ("Exif IFD", [4], None, "A pointer to the Exif IFD"),
    34675:  ("ICC Profile", [7], None, "ICC profile data"),
    34735:  ("GeoKeyDirectoryTag", [3], None, "Used in interchangeable GeoTIFF files"),
    34736:  ("GeoDoubleParamsTag", [12], None, "Used in interchangeable GeoTIFF files"),
    34737:  ("GeoAsciiParamsTag", [2], None, "Used in interchangeable GeoTIFF files"),
    34853:  ("GPS IFD", [4], None, "A pointer to the Exif-related GPS Info IFD"),
    34908:  ("HylaFAX FaxRecvParams", [4], None, "Used by HylaFAX"),
    34909:  ("HylaFAX FaxSubAddress", [2], None, "Used by HylaFAX"),
    34910:  ("HylaFAX FaxRecvTime", [4], None, "Used by HylaFAX"),
    37724:  ("ImageSourceData", [7], None, "Used by Adobe Photoshop"),
    40965:  ("Interoperability IFD", [4], None, "A pointer to the Exif-related Interoperability IFD"),
    42112:  ("GDAL_METADATA", [2], None, "Used by the GDAL library, holds an XML list of name=value 'metadata' values about the image as a whole, and about specific samples"),
    42113:  ("GDAL_NODATA", [2], None, "Used by the GDAL library, contains an ASCII encoded nodata or background pixel value"),
    50215:  ("Oce Scanjob Description", [2], None, "Used in the Oce scanning process"),
    50216:  ("Oce Application Selector", [2], None, "Used in the Oce scanning process"),
    50217:  ("Oce Identification Number", [2], None, "Used in the Oce scanning process"),
    50218:  ("Oce ImageLogic Characteristics", [2], None, "Used in the Oce scanning process"),
    50706:  ("DNGVersion", [3], None, "Used in IFD 0 of DNG files"),
    50707:  ("DNGBackwardVersion", [3], None, "Used in IFD 0 of DNG files"),
    50708:  ("UniqueCameraModel", [2], None, "Used in IFD 0 of DNG files"),
    50709:  ("LocalizedCameraModel", [2,3], None, "Used in IFD 0 of DNG files"),
    50710:  ("CFAPlaneColor", [3], None, "Used in Raw IFD of DNG files"),
    50711:  ("CFALayout", [1], None, "Used in Raw IFD of DNG files"),
    50712:  ("LinearizationTable", [1], None, "Used in Raw IFD of DNG files"),
    50713:  ("BlackLevelRepeatDim", [1], None, "Used in Raw IFD of DNG files"),
    50714:  ("BlackLevel", [1,4,5], None, "Used in Raw IFD of DNG files"),
    50715:  ("BlackLevelDeltaH", [10], None, "Used in Raw IFD of DNG files"),
    50716:  ("BlackLevelDeltaV", [10], None, "Used in Raw IFD of DNG files"),
    50717:  ("WhiteLevel", [1,4], None, "Used in Raw IFD of DNG files"),
    50718:  ("DefaultScale", [5], None, "Used in Raw IFD of DNG files"),
    50719:  ("DefaultCropOrigin", [1,4,5], None, "Used in Raw IFD of DNG files"),
    50720:  ("DefaultCropSize", [1,4,5], None, "Used in Raw IFD of DNG files"),
    50721:  ("ColorMatrix1", [10], None, "Used in IFD 0 of DNG files"),
    50722:  ("ColorMatrix2", [10], None, "Used in IFD 0 of DNG files"),
    50723:  ("CameraCalibration1", [10], None, "Used in IFD 0 of DNG files"),
    50724:  ("CameraCalibration2", [10], None, "Used in IFD 0 of DNG files"),
    50725:  ("ReductionMatrix1", [10], None, "Used in IFD 0 of DNG files"),
    50726:  ("ReductionMatrix2", [10], None, "Used in IFD 0 of DNG files"),
    50727:  ("AnalogBalance", [5], None, "Used in IFD 0 of DNG files"),
    50728:  ("AsShotNeutral", [1,5], None, "Used in IFD 0 of DNG files"),
    50729:  ("AsShotWhiteXY", [5], None, "Used in IFD 0 of DNG files"),
    50730:  ("BaselineExposure", [10], None, "Used in IFD 0 of DNG files"),
    50731:  ("BaselineNoise", [10], None, "Used in IFD 0 of DNG files"),
    50732:  ("BaselineSharpness", [10], None, "Used in IFD 0 of DNG files"),
    50733:  ("BayerGreenSplit", [4], None, "Used in Raw IFD of DNG files"),
    50734:  ("LinearResponseLimit", [5], None, "Used in IFD 0 of DNG files"),
    50735:  ("CameraSerialNumber", [2], None, "Used in IFD 0 of DNG files"),
    50736:  ("LensInfo", [5], None, "Used in IFD 0 of DNG files"),
    50737:  ("ChromaBlurRadius", [5], None, "Used in Raw IFD of DNG files"),
    50738:  ("AntiAliasStrength", [5], None, "Used in Raw IFD of DNG files"),
    50740:  ("DNGPrivateData", [3], None, "Used in IFD 0 of DNG files"),
    50741:  ("MakerNoteSafety", [1], None, "Used in IFD 0 of DNG files"),
    50778:  ("CalibrationIlluminant1", [1], None, "Used in IFD 0 of DNG files"),
    50779:  ("CalibrationIlluminant2", [1], None, "Used in IFD 0 of DNG files"),
    50780:  ("BestQualityScale", [5], None, "Used in Raw IFD of DNG files"),
    50784:  ("Alias Layer Metadata", [2], None, "Alias Sketchbook Pro layer usage description"),
    # XP tags
    0x9c9b: ("XPTitle", [4], None, ""),
    0x9c9c: ("XPComment", [4], None, ""),
    0x9c9d: ("XPAuthor", [4], None, ""),
    0x9c9e: ("XPKeywords", [4], None, ""),
    0x9c9f: ("XPSubject", [4], None, ""),
    0xea1c: ("Padding", [7], None, ""),
    0xea1d: ("OffsetSchema", [9], None, ""),
}

# Exif tags
exfT = {
    33434: ("ExposureTime", [5], None, "Exposure time, given in seconds"),
    33437: ("FNumber", [5], None, "The F number"),
    34850: ("ExposureProgram", [1], (0,), "The class of the program used by the camera to set exposure when the picture is taken"),
    34852: ("SpectralSensitivity", [2], None, "Indicates the spectral sensitivity of each channel of the camera used"),
    34855: ("ISOSpeedRatings", [1], None, "Indicates the ISO Speed and ISO Latitude of the camera or input device as specified in ISO 12232"),
    34856: ("OECF", [7], None, "Indicates the Opto-Electric Conversion Function (OECF) specified in ISO 14524"),
    34867: ("ISOSpeed", [4], None, "This tag indicates the ISO speed value of a camera or input device that is defined in ISO 12232."),
    36864: ("ExifVersion", [7], b"0220", "The version of the supported Exif standard"),
    36867: ("DateTimeOriginal", [2], None, "The date and time when the original image data was generated"),
    36868: ("DateTimeDigitized", [2], None, "The date and time when the image was stored as digital data"),
    37121: ("ComponentsConfiguration", [7], None, "Specific to compressed data; specifies the channels and complements PhotometricInterpretation"),
    37122: ("CompressedBitsPerPixel", [5], None, "Specific to compressed data; states the compressed bits per pixel"),
    37377: ("ShutterSpeedValue", [11], None, "Shutter speed"),
    37378: ("ApertureValue", [5], None, "The lens aperture"),
    37379: ("BrightnessValue", [5], None, "The value of brightness"),
    37380: ("ExposureBiasValue", [11], None, "The exposure bias"),
    37381: ("MaxApertureValue", [5], None, "The smallest F number of the lens"),
    37382: ("SubjectDistance", [5], None, "The distance to the subject, given in meters"),
    37383: ("MeteringMode", [1], (0,), "The metering mode"),
    37384: ("LightSource", [1], (0,), "The kind of light source"),
    37385: ("Flash", [1], None, "Indicates the status of flash when the image was shot"),
    37386: ("FocalLength", [5], None, "The actual focal length of the lens, in mm"),
    37396: ("SubjectArea", [1], None, "Indicates the location and area of the main subject in the overall scene"),
    37500: ("MakerNote", [7], None, "Manufacturer specific information"),
    37510: ("UserComment", [7], None, "Keywords or comments on the image; complements ImageDescription"),
    37520: ("SubsecTime", [2], None, "A tag used to record fractions of seconds for the DateTime tag"),
    37521: ("SubsecTimeOriginal", [2], None, "A tag used to record fractions of seconds for the DateTimeOriginal tag"),
    37522: ("SubsecTimeDigitized", [2], None, "A tag used to record fractions of seconds for the DateTimeDigitized tag"),
    40960: ("FlashpixVersion", [7], b"0100", "The Flashpix format version supported by a FPXR file"),
    40961: ("ColorSpace", [1], None, "The color space information tag is always recorded as the color space specifier"),
    40962: ("PixelXDimension", [1,4], None, "Specific to compressed data; the valid width of the meaningful image"),
    40963: ("PixelYDimension", [1,4], None, "Specific to compressed data; the valid height of the meaningful image"),
    40964: ("RelatedSoundFile", [2], None, "Used to record the name of an audio file related to the image data"),
    41483: ("FlashEnergy", [5], None, "Indicates the strobe energy at the time the image is captured, as measured in Beam Candle Power Seconds"),
    41484: ("SpatialFrequencyResponse", [7], None, "Records the camera or input device spatial frequency table and SFR values in the direction of image width, image height, and diagonal direction, as specified in ISO 12233"),
    41486: ("FocalPlaneXResolution", [5], None, "Indicates the number of pixels in the image width (X) direction per FocalPlaneResolutionUnit on the camera focal plane"),
    41487: ("FocalPlaneYResolution", [5], None, "Indicates the number of pixels in the image height (Y) direction per FocalPlaneResolutionUnit on the camera focal plane"),
    41488: ("FocalPlaneResolutionUnit", [1], (2,), "Indicates the unit for measuring FocalPlaneXResolution and FocalPlaneYResolution"),
    41492: ("SubjectLocation", [2], None, "Indicates the location of the main subject in the scene"),
    41493: ("ExposureIndex", [5], None, "Indicates the exposure index selected on the camera or input device at the time the image is captured"),
    41495: ("SensingMethod", [1], None, "Indicates the image sensor type on the camera or input device"),
    41728: ("FileSource", [7], b"3", "Indicates the image source"),
    41729: ("SceneType", [7], b"1", "Indicates the type of scene"),
    41730: ("CFAPattern", [7], None, "Indicates the color filter array (CFA) geometric pattern of the image sensor when a one-chip color area sensor is used"),
    41985: ("CustomRendered", [1], (0,), "Indicates the use of special processing on image data, such as rendering geared to output"),
    41986: ("ExposureMode", [1], None, "Indicates the exposure mode set when the image was shot"),
    41987: ("WhiteBalance", [1], None, "Indicates the white balance mode set when the image was shot"),
    41988: ("DigitalZoomRatio", [5], None, "Indicates the digital zoom ratio when the image was shot"),
    41989: ("FocalLengthIn35mmFilm", [1], None, "Indicates the equivalent focal length assuming a 35mm film camera, in mm"),
    41990: ("SceneCaptureType", [1], (0,), "Indicates the type of scene that was shot"),
    41991: ("GainControl", [1], None, "Indicates the degree of overall image gain adjustment"),
    41992: ("Contrast", [1], (0,), "Indicates the direction of contrast processing applied by the camera when the image was shot"),
    41993: ("Saturation", [1], (0,), "Indicates the direction of saturation processing applied by the camera when the image was shot"),
    41994: ("Sharpness", [1], (0,), "Indicates the direction of sharpness processing applied by the camera when the image was shot"),
    41995: ("DeviceSettingDescription", [7], None, "This tag indicates information on the picture-taking conditions of a particular camera model"),
    41996: ("SubjectDistanceRange", [1], None, "Indicates the distance to the subject"),
    42016: ("ImageUniqueID", [2], None, "Indicates an identifier assigned uniquely to each image"),
    42033: ("BodySerialNumber", [2], None, "This tag records the serial number of the body of the camera that was used in photography as an ASCII string."),
    0xea1c: ("Padding", [7], None, ""),
}
_exfT = dict(
    (name, (tag, types, default, comment))
    for tag, (name, types, default, comment) in exfT.items()
)

# GPS tags
gpsT = {
    0:  ("GPSVersionID", [3], (2,2,0,0), "Indicates the version of GPSInfoIFD"),
    1:  ("GPSLatitudeRef", [2], None, "Indicates whether the latitude is north or south latitude"),
    2:  ("GPSLatitude", [5], None, "Indicates the latitude"),
    3:  ("GPSLongitudeRef", [2], None, "Indicates whether the longitude is east or west longitude"),
    4:  ("GPSLongitude", [5], None, "Indicates the longitude"),
    5:  ("GPSAltitudeRef", [3], None, "Indicates the altitude used as the reference altitude"),
    6:  ("GPSAltitude", [5], None, "Indicates the altitude based on the reference in GPSAltitudeRef"),
    7:  ("GPSTimeStamp", [5], None, "Indicates the time as UTC (Coordinated Universal Time)"),
    8:  ("GPSSatellites", [2], None, "Indicates the GPS satellites used for measurements"),
    9:  ("GPSStatus", [2], None, "Indicates the status of the GPS receiver when the image is recorded"),
    10: ("GPSMeasureMode", [2], None, "Indicates the GPS measurement mode"),
    11: ("GPSDOP", [5], None, "Indicates the GPS DOP (data degree of precision)"),
    12: ("GPSSpeedRef", [2], b'K\x00', "Indicates the unit used to express the GPS receiver speed of movement"),
    13: ("GPSSpeed", [5], None, "Indicates the speed of GPS receiver movem5nt"),
    14: ("GPSTrackRef", [2], b'T\x00', "Indicates the reference for giving the direction of GPS receiver movement"),
    15: ("GPSTrack", [5], None, "Indicates the direction of GPS receiver movement"),
    16: ("GPSImgDirectionRef", [2], b'T\x00', "Indicates the reference for giving the direction of the image when it is captured"),
    17: ("GPSImgDirection", [5], None, "Indicates the direction of the image when it was captured"),
    18: ("GPSMapDatum", [2], None, "Indicates the geodetic survey data used by the GPS receiver"),
    19: ("GPSDestLatitudeRef", [2], None, "Indicates whether the latitude of the destination point is north or south latitude"),
    20: ("GPSDestLatitude", [5], None, "Indicates the latitude of the destination point"),
    21: ("GPSDestLongitudeRef", [2], None, "Indicates whether the longitude of the destination point is east or west longitude"),
    22: ("GPSDestLongitude", [5], None, "Indicates the longitude of the destination point"),
    23: ("GPSDestBearingRef", [2], None, "Indicates the reference used for giving the bearing to the destination point"),
    24: ("GPSDestBearing", [5], None, "Indicates the bearing to the destination point"),
    25: ("GPSDestDistanceRef", [2], None, "Indicates the unit used to express the distance to the destination point"),
    26: ("GPSDestDistance", [5], None, "Indicates the distance to the destination point"),
    27: ("GPSProcessingMethod", [7], None, "A character string recording the name of the method used for location finding"),
    28: ("GPSAreaInformation", [7], None, "A character string recording the name of the GPS area"),
    29: ("GPSDateStamp", [2], None, "A character string recording date and time information relative to UTC (Coordinated Universal Time)"),
    30: ("GPSDifferential", [1], None, "Indicates whether differential correction is applied to the GPS receiver"),
}
_gpsT = dict(
    (name, (tag, types, default, comment))
    for tag, (name, types, default, comment) in gpsT.items()
)

# Interoperability tags
itrT = {
    0x0001: ("InteropIndex", [2], b"R03\x00", ""),
    0x0002: ("InteropVersion", [7], None, ""),
    0x1000: ("RelatedImageFileFormat", [2], None, ""),
    0x1001: ("RelatedImageWidth", [4], None, ""),
    0x1002: ("RelatedImageHeight", [4], None, ""),
}
_itrT = dict(
    (name, (tag, types, default, comment))
    for tag, (name, types, default, comment) in itrT.items()
)

_BY_TAG = dict(
    reduce(
        tuple.__add__,
        (tuple(dic.items()) for dic in [bTT, xTT, pTT])
    )
)

_BY_NAME = dict(
    (name, (tag, types, default, comment))
    for tag, (name, types, default, comment) in _BY_TAG.items()
)


def get(tag_or_key):
    if isinstance(tag_or_key, (bytes, str)):
        for dic in [_BY_NAME, _exfT, _gpsT, _itrT]:
            if tag_or_key in dic:
                tag, types, default, comment = dic[tag_or_key]
                return tag, (tag_or_key, types, default, comment)
    else:
        for dic in [_BY_TAG, exfT, gpsT, itrT]:
            if tag_or_key in dic:
                return tag_or_key, dic[tag_or_key]

    return False, ("Undefined", [7], None, "Undefined tag %r" % tag_or_key)
