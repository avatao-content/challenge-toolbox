#!/usr/bin/env python3
# This is an internal script for deploying simple images for challenge infrastructures.
# Do not use this for developing challenges.

import logging
import sys
from typing import Optional, Tuple

from toolbox.docker.build import build_image
from toolbox.docker.utils import get_image_url, mirror_images, push_images
from toolbox.utils import counted_error_at_exit, init_logger


def get_sys_args() -> Tuple[str, str, Optional[str]]:
    if not 3 <= len(sys.argv) <= 4:
        logging.info('Usage: %s <image-name> <build-path> [dockerfile]', sys.argv[0])
        sys.exit(1)

    image = sys.argv[1]
    path = sys.argv[2]
    dockerfile = sys.argv[3] if len(sys.argv) >= 4 else None

    return image, path, dockerfile


def run(image: str, path: str, dockerfile: Optional[str] = None):
    image = get_image_url(image)
    build_image(image, path, dockerfile)
    push_images([image])
    mirror_images([image])


if __name__ == '__main__':
    init_logger()
    run(*get_sys_args())
    counted_error_at_exit()
