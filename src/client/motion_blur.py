from src.log import log, warn
from src.client.types.vector import Vector3, derive


def lerp(a: int | float, b: int | float, t: int | float) -> int | float: return (1 - t) * a + t * b


class MotionblurManager:
    def __init__(self, instance):
        self.instance = instance
        self.enabled = True

        self.camera_pos_last = Vector3(0, 0, 0)
        self.camera_hpr_last = Vector3(0, 0, 0)
        self.camera_diff_last = 0.0

        self.instance.new_task('mt_blr_task', self.mt_blr_task)


    def disable(self):
        self.enabled = False


    def enable(self):
        self.enabled = True


    def mt_blr_task(self, task):
        if not self.enabled: return task.cont

        current_cam_hpr = derive(self.instance.camera.get_hpr())

        diff_hpr = current_cam_hpr.magnitude(self.camera_hpr_last)

        diff = lerp(self.camera_diff_last, diff_hpr, 1.0)

        self.instance.post_processing_manager.set_sharpen_image(diff)

        self.camera_hpr_last = current_cam_hpr
        return task.cont
