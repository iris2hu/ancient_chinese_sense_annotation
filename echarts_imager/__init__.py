from pathlib import Path
from typing import IO, Any, Dict, Optional, Tuple
import json
from io import BytesIO
from subprocess import run, STDOUT
from tempfile import TemporaryFile
from PIL import Image
try:
    from IPython import get_ipython
    from IPython.display import display, HTML
    CAN_DISPLAY = get_ipython().__class__.__name__ != 'NoneType'
except ImportError:
    CAN_DISPLAY = False

NODE_PATH = '/media/disk2/Programs/node-v16.15.0-linux-x64/bin/node'
JS_PATH = '/media/disk2/wangzhaoji/Projects/echarts-imager/index'


class EChartsError(Exception):
    pass


class EChartsOptionError(EChartsError):
    pass


class EChartsFormatError(EChartsError):
    pass


class EChartsImageError(EChartsError):
    pass


class ECharts:
    __option: Optional[Dict[str, Any]]
    __image: Optional[Image.Image]
    __svg: Optional[str]
    __format: str
    __width: int
    __height: int
    __device_pixel_ratio: int

    def __init__(self,
                 option: Optional[Dict[str, Any]] = None,
                 size: Tuple[int, int] = (1024, 768),
                 format: str = 'png',
                 device_pixel_ratio: int = 1,
                 auto_render: bool = True):
        # Initialize properties
        self.__option = None
        self.__image = None
        self.__svg = None
        self.__format = ''
        self.__width = 0
        self.__height = 0
        self.__device_pixel_ratio = 0
        # Set properties
        self.set_format(format)
        self.set_device_pixel_ratio(device_pixel_ratio)
        if size:
            self.set_size(size)
        if option:
            self.set_option(option, auto_render)

    @property
    def width(self) -> int:
        '''The width of the chart file.'''
        return self.__width

    @property
    def height(self) -> int:
        '''The height of the chart file.'''
        return self.__height

    @property
    def size(self) -> Tuple[int, int]:
        '''The size of the chart file. (width, height)'''
        return self.__width, self.__height

    @property
    def device_pixel_ratio(self) -> int:
        '''The device pixel ratio of the chart file (only valid for bitmap format).'''
        return self.__device_pixel_ratio

    @property
    def format(self) -> str:
        '''The format of the chart file. (default: png)'''
        return self.__format

    @property
    def image(self) -> Optional[Image.Image]:
        '''The Pillow Image object of the chart file.'''
        return self.__image

    @property
    def svg(self) -> Optional[str]:
        '''The SVG string of the chart file.'''
        return self.__svg

    @property
    def option(self) -> Optional[Dict[str, Any]]:
        '''The ECharts format option of the chart file.'''
        return self.__option

    def set_device_pixel_ratio(self, ratio: int) -> 'ECharts':
        '''Set the device pixel ratio of the chart file (only valid for bitmap format).'''
        if not ratio:
            raise EChartsImageError(
                'The device pixel ratio of the chart file must be greater than zero.'
            )
        self.__device_pixel_ratio = ratio
        return self

    def set_format(self, format: str) -> 'ECharts':
        if not format:
            raise EChartsFormatError('The format of the chart file is None.')
        self.__format = format
        return self

    def set_size(self, size: Tuple[int, int]) -> 'ECharts':
        '''The size of the chart file. (width, height)'''
        width, height = size
        self.__width = width
        self.__height = height
        return self

    def set_option(self,
                   option: Dict[str, Any],
                   auto_render: bool = True) -> 'ECharts':
        '''Set the option and generate the chart file.'''
        self.__option = option
        if auto_render:
            self.render()
        return self

    def render(self) -> 'ECharts':
        '''Render the chart file.'''
        if self.__format == 'svg':
            self.__render_svg()
        else:
            self.__render_image()
        return self

    def resize(self,
               size: Tuple[int, int],
               auto_render: bool = True) -> 'ECharts':
        '''Regenerate the chart file with a new size.'''
        width, height = size
        is_size_changed = False
        if width != self.__width or height != self.__height:
            self.__width = width
            self.__height = height
            is_size_changed = True
        if auto_render and self.__option and is_size_changed:
            self.render()
        return self

    def save(self, path: str, log: bool = True) -> None:
        '''Save the chart file to the path.'''
        path_object = Path(path)
        file_parent_path = path_object.parent.absolute()
        filename = path_object.name
        filename_parts = filename.split('.')
        name = filename_parts[0]
        ext = self.__format
        if len(filename_parts) > 1:
            ext = filename_parts[1]
        if ext != self.__format:
            raise EChartsFormatError(
                'The format of the chart file is not the same as the format (extension) of the path.'
            )
        path = f'{file_parent_path}/{name}.{ext}'
        if self.__format == 'svg':
            if not self.__svg:
                raise EChartsImageError('The svg data of Echarts is None.')
            with open(path, 'w') as fp:
                fp.write(self.__svg)
        elif self.__image:
            self.__image.save(path)
        else:
            raise EChartsImageError('The image data of Echarts is None.')
        if log:
            print(f'The chart file is saved to {path}')

    def show(self) -> None:
        '''Show the chart file.'''
        if self.__format == 'svg':
            if not self.__svg:
                raise EChartsImageError('The svg data of Echarts is None.')
            if CAN_DISPLAY:
                display(HTML(self.__svg))
            else:
                print(self.__svg)
        else:
            if not self.__image:
                raise EChartsImageError('The image data of Echarts is None.')
            if CAN_DISPLAY:
                display(self.__image)
            else:
                self.__image.show()

    def __render_svg(self):
        buf = self.__generate_chart_bytes()
        self.__svg = buf.decode('utf-8')

    def __render_image(self):
        buf = self.__generate_chart_bytes()
        self.__image = Image.open(BytesIO(buf))

    def __generate_chart_bytes(self):  # sourcery skip: use-named-expression
        if self.__option is None:
            raise EChartsOptionError('The option of Echarts is None.')
        option_json = json.dumps(self.__option, ensure_ascii=False)
        with TemporaryFile() as fp:
            stdout_bytes = self.__run_cli_program(option_json, fp)
        start_idx = stdout_bytes.find(b'{"type":"Buffer"')
        info = (stdout_bytes if start_idx == -1 else
                stdout_bytes[:start_idx]).decode('utf-8')
        if info:
            print(info)
        if start_idx == -1:
            return bytes()
        buf_json_bytes = stdout_bytes[start_idx:]
        buf_data = json.loads(buf_json_bytes)['data']
        return bytes(buf_data)

    def __run_cli_program(self, option_json: str, fp: IO[bytes]):
        args = [
            NODE_PATH, JS_PATH, '-b', '-f', self.__format, '-w',
            str(self.__width), '-h',
            str(self.__height), '-d',
            str(self.__device_pixel_ratio)
        ]
        run(args,
            input=option_json,
            universal_newlines=True,
            stdout=fp,
            stderr=STDOUT)
        fp.seek(0)
        return fp.read()

    def _repr_html_(self):
        if self.__format == 'svg' and self.__svg:
            return display(HTML(self.__svg))
        elif self.__format == 'svg' or not self.__image:
            return f'&lt;ECharts unrendered format={self.format} size={self.__width}×{self.__height}&gt;'
        else:
            return display(self.__image)
