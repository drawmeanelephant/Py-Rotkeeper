import shutil
import logging

logger = logging.getLogger(__name__)

class MissingFrontendDependencyError(Exception):
    pass

def require_frontend_bins(*bins: str):
    missing_bins = []
    for bin_name in bins:
        if shutil.which(bin_name) is None:
            missing_bins.append(bin_name)

    if missing_bins:
        for bin_name in missing_bins:
            logger.error(f"Required frontend binary '{bin_name}' not found in PATH.")
        raise MissingFrontendDependencyError(f"Missing frontend dependencies: {', '.join(missing_bins)}")

def check_node():
    require_frontend_bins('node')

def check_sass():
    # Sass can be 'sass' (Dart Sass) or 'node-sass'
    if shutil.which('sass') is None and shutil.which('node-sass') is None:
        logger.error("Neither 'sass' nor 'node-sass' found in PATH.")
        raise MissingFrontendDependencyError("Missing frontend dependency: 'sass' or 'node-sass'")
