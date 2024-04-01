from apps import base_setting

from apps.web import models


def run():
    # exit = models.fees.objects.filter(cate=1, title="免费版").exists()
    # if not exit:
    #     models.fees.objects.create(cate=1, title="免费版", prices="0", create_project_num="3", space_size="20",
    #                                file_size="5", project_member_num="2")
    models.UserInfo.objects.filter(id=2).delete()


if __name__ == '__main__':
    run()
