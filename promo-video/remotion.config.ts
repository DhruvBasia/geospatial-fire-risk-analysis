import {Config} from '@remotion/cli/config';

// PNG frames keep the thin map lines and gradients clean before H.264 encoding.
Config.setVideoImageFormat('png');
Config.setOverwriteOutput(true);
