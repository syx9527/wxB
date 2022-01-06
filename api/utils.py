import hashlib
import logging
import os
import random
import time
import uuid

from django.conf import settings
from django.core.mail import send_mail

from imageserver.utils import conf

logger = logging.getLogger('django')


def send_message(recipient_list, subject, message, ):
    from_email = settings.EMAIL_HOST_USER
    # 值1：  邮件标题   值2： 邮件主体
    # 值3： 发件人      值4： 收件人
    res = send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
    if res == 1:
        message = True

    else:
        message = False

    return message


class PictureStorageToolClass(object):
    """文件存储工具类"""

    def __init__(self):
        pass
        # self.randomlength = 16

    # 计算图片的md5
    def calculate_image_md5(self, file):
        md5_obj = hashlib.md5()
        for chunk in file.chunks():
            md5_obj.update(chunk)
        return md5_obj.hexdigest()

    # 检验文件类型(已流的方式判断,可以用于pdf等格式的数据上传)
    def precise_type(self, file):
        """
        类型:
        图片:image/png image/jpeg等,
        文本:text/plain
        pdf:application/pdf
        docx:application/vnd.openxmlformats-officedocument.wordprocessingml.document
        doc:application/msword

        django中file的方法:[image.file, image.field_name, image.name, image.content_type,
                  image.size, image.charset, image.content_type_extra]
        """
        # pip install python_magic来判断文件类型
        # f = magic.Magic(mime=True, uncompress=True)
        # 方式1: buffer_type = f.from_buffer(open('/home/vir/imageserver/image/heading/6f3f73b5-a258-496e-a3df-1bb90d4dd483_5.png', 'rb').read(1024))
        # 方式2: file_type = f.from_file('/home/vir/imageserver/image/heading/6f3f73b5-a258-496e-a3df-1bb90d4dd483_5.png')

        file_type = file.content_type
        return file_type

    # 检测文件类型(如果是图片判断后缀)
    def judge_type(self, image_type):
        image_type_list = ['jpeg', 'jpg', 'png', 'pdf', 'tga', 'tif', 'svg', 'gif', 'bmp']
        if image_type not in image_type_list:
            return 0
        return 1

    # 限制文件大小(5M)
    def file_size(self, image_size):
        if image_size > conf.IMAGE_SIZE:
            return 0
        return 1

    # 返回图片存储路径
    def storage_path(self, folder):
        """
        folder:
        图片存储文件路径文件夹命名:
        头像图片:heading
        面料图片:fabric
        作品图片:style
        其他图片:rest
        """
        root_path = os.path.join(conf.IMAGE_STORAGE_PATH, folder)
        # 如果没有创建
        if not os.path.exists(root_path):
            os.makedirs(root_path)

        return root_path

    # 保存图片
    def save_iamge(self, root_path, image_name, image):
        """
        root_path: 图片路径
        image_name:图片名称
        iamge:前端传递过来的image对象
        """
        uuid_iamge_name = None
        file_path_name = None

        # 保存
        try:
            uuid_iamge_name = str(uuid.uuid4()) + '_' + image_name  # 生成一个新的不重复的名称
            file_path_name = root_path + '/' + uuid_iamge_name  # 图片的完整路径(仅仅是在我们服务器保存的位置,不是我们外部访问的路径)

            with open(file_path_name, 'wb') as f:
                for line in image.chunks():
                    f.write(line)
        except Exception as e:
            logger.error(e)
            return 0, 0

        return uuid_iamge_name, file_path_name


def upload_image(file, upload_to):
    ext = os.path.splitext(file.name)[1]

    file_name = time.strftime('%Y%m%d', time.localtime(time.time())) + str(random.randint(10000, 99999))
    # 重新生成文件名
    file.name = file_name + ext

    dir = os.path.join(settings.MEDIA_ROOT, "foreign_workers/")
    destination = open(os.path.join(dir, file.name),
                       'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
