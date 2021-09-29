def set_up_django_project(project_name, project_path, env_file=None):

    """
    Sets up a Django project and optionally loads in environment variables from a .env file.

    Usage::
        PROJECT_FOLDER = os.path.abspath(os.curdir)
        set_up_django_project(
            "my_project_name",
            PROJECT_FOLDER,
            env_file="my_env_file.env"
        )

    :param project_name:
    :param project_path:
    :param env_file:
    :return:
    """

    import django
    import os
    import sys
    from dotenv import load_dotenv
    from pathlib import Path

    from rasterio.env import GDALDataFinder

    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    os.environ["DJANGO_SETTINGS_MODULE"] = "{}.settings".format(project_name)
    os.environ["GDAL_DATA"] = GDALDataFinder().search()

    if env_file:
        load_dotenv(Path(env_file).expanduser())

    for path in list(sys.path):
        if "/apps/prod" in path:
            del sys.path[sys.path.index(path)]

    for p in [project_path, "{}/src".format(project_path)]:
        p_full = str(Path(p).expanduser())
        if p_full in sys.path:
            del sys.path[p_full]
        sys.path.insert(0, p_full)

    for folder in os.listdir("{}/src".format(project_path)):
        sys.path.insert(0, os.path.join(project_path, "src", folder))

    django.setup()