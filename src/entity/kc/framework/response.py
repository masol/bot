from attrs import define, field
from entity.entity import Entity
from entity.env import Env
from os import path
from datetime import datetime
from PIL import Image
import numpy as np

# from .dumper import Dumper

transparent_formats = ["png", "webp"]
image_formats = ["jpg", "jpeg"] + transparent_formats
IMG_PREFIX = "img_"


# 保存图片信息．
@define(slots=True)
class ImageInfo:
    # 图片文件名．
    filename: str = field(default="")
    # 图片宽度．
    width: int = field(default=256)
    # 图片高度．
    height: int = field(default=256)
    # 是否有透明通道.
    transparent: bool = field(default=False)


@define(slots=True)
class Response(Entity):
    type: str = field(default="Response")

    # # 服务于mode(例如页面),跟踪一个流程行为的创建上下文．
    # genbhctx: Dumper = field(default=None)

    # 项目的输出根目录．
    target: str = field(default=None)

    # 获取输出目录．
    def target_dir(self, *args):
        return path.join(self.target, *args)

    def calc_var(self, req, varname, template_name: str):
        if varname == "current_year":
            return datetime.now().year
        elif varname == "project_name":  # @TODO: 在输入文件中定义option.这里使用当前的项目名称．
            return self.name

    def get_imgpath(self, req, filename):
        raise ValueError("未实现图片路径获取．")

    # fnparts为图片文件名的各部分(不包括目录与后缀)．
    def get_imgvalue(self, fnparts: list, imgInfo):
        raise ValueError("未实现图片值获取．")

    # 确认需要的图片存在，如果不存在，创建之．
    def ensure_img(self, req, img_info: ImageInfo, template_name: str):
        filepath = self.get_imgpath(req, img_info.filename)
        if not path.exists(filepath):
            directory = path.dirname(filepath)
            Env.mkdirs(directory)
            pixel_data = np.random.randint(
                0,
                255,
                (img_info.width, img_info.height, 4 if img_info.transparent else 3),
                dtype=np.uint8,
            )
            # 创建一个新的图像
            imgobj = Image.fromarray(pixel_data)
            # 保存为PNG格式的图片
            imgobj.save(filepath)

    def calc_img_var(self, req, varname, template_name: str):
        tokens = varname[len(IMG_PREFIX) :].split("__")
        w = 256
        h = 256
        suffix = "jpg"
        transparent = False
        filename = ""
        if len(tokens) > 1:  # 定义了图片尺寸．
            size = tokens[0].split("_")
            w = int(size[0])
            if len(size) > 1:
                h = int(size[1])
            else:
                h = w
        fnparts = tokens[-1].split("_")
        if fnparts[-1].lower() in image_formats:
            suffix = fnparts[-1].lower()
            transparent = suffix in transparent_formats
            fnparts.pop()
        filename = "/".join(fnparts) + "." + suffix
        img_info = ImageInfo(
            filename=filename, width=w, height=h, transparent=transparent
        )
        self.ensure_img(req, img_info, template_name)
        return self.get_imgvalue(fnparts, img_info)

    # 获取变量的值．这里才会真正触发计算变量．使用HORN SAT求解．
    # 返回确定之后的变量．如果有变量无法确定，抛出异常．
    def get_vars(
        self, req: "Requirement", undeclared: dict, template_name: str, base_vars=None
    ) -> dict:
        cfg_env = req.store.env
        const_dict = {"compath": "src/components"}
        const_vars = set(const_dict.keys())
        env_vars = {"subdir"}
        if not isinstance(base_vars, dict):
            base_vars = {}
        ret_vars = dict()
        for key in undeclared:
            if key in base_vars:
                ret_vars[key] = base_vars[key]
            elif key in const_vars:
                ret_vars[key] = const_dict[key]
            elif key in env_vars:
                ret_vars[key] = cfg_env.getattr(key)
            elif key.startswith(IMG_PREFIX):
                ret_vars[key] = self.calc_img_var(req, key, template_name)
            else:
                varvalue = self.calc_var(req, key, template_name)
                if varvalue == None:
                    raise ValueError(f"无法识别模板{template_name}中定义的变量:{key}")
                else:
                    ret_vars[key] = varvalue
                # print("img_info=", img_info)
        return ret_vars
