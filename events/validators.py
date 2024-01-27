from django.core.exceptions import ValidationError

def validate_image_size(image):
    file_size = image.size
    limit_kb = 1024
    if file_size > limit_kb * 1024:
        raise ValidationError("Max size of file is %s KB" % limit_kb)