with import <nixpkgs> { };

let
  twitter_common_app = buildPythonPackage rec {
    name = "twitter.common.app-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.app/${name}.tar.gz";
      md5 = "d571088eaaf476e3ac1b3cc72b49970e";
    };

    propagatedBuildInputs = [
      twitter_common_util
      twitter_common_process
      twitter_common_log
      twitter_common_collections
      twitter_common_contextutil
      twitter_common_string
      twitter_common_options
      twitter_common_dirutil
      twitter_common_lang
    ];
  };

  twitter_common_util = buildPythonPackage rec {
    name = "twitter.common.util-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.util/${name}.tar.gz";
      md5 = "6e3dac3193d5fb9befd3c2316cbaa4bc";
    };

    propagatedBuildInputs = [
      twitter_common_contextutil
      twitter_common_dirutil
      twitter_common_lang
    ];
  };

  twitter_common_contextutil = buildPythonPackage rec {
    name = "twitter.common.contextutil-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.contextutil/${name}.tar.gz";
      md5 = "00119c77f8103c1ddb46a21b9fef7377";
    };

    propagatedBuildInputs = [
      twitter_common_dirutil
      twitter_common_lang
    ];
  };

  twitter_common_dirutil = buildPythonPackage rec {
    name = "twitter.common.dirutil-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.dirutil/${name}.tar.gz";
      md5 = "344648a50a9e337647ecd3129cabc128";
    };

    propagatedBuildInputs = [ twitter_common_lang ];
  };

  twitter_common_lang = buildPythonPackage rec {
    name = "twitter.common.lang-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.lang/${name}.tar.gz";
      md5 = "d4f9ad4fc0f1974570d575f25713ebe6";
    };
  };

  twitter_common_process = buildPythonPackage rec {
    name = "twitter.common.process-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.process/${name}.tar.gz";
      md5 = "cc5cb50b1bb596224940d5d5e479d4c6";
    };

    propagatedBuildInputs = [
      twitter_common_string
      twitter_common_lang
    ];
  };

  twitter_common_string = buildPythonPackage rec {
    name = "twitter.common.string-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.string/${name}.tar.gz";
      md5 = "78d4fa8fb97d4da2e88cbbebbaeb98f9";
    };

    propagatedBuildInputs = [ twitter_common_lang ];
  };

  twitter_common_log = buildPythonPackage rec {
    name = "twitter.common.log-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.log/${name}.tar.gz";
      md5 = "27493c9faa8865c8892b56142adc3474";
    };

    propagatedBuildInputs = [
      twitter_common_options
      twitter_common_dirutil
      twitter_common_lang
    ];
  };

  twitter_common_options = buildPythonPackage rec {
    name = "twitter.common.options-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.options/${name}.tar.gz";
      md5 = "80b7ea8739d9cbe90ecf1f446e3e11f8";
    };
  };

  twitter_common_collections = buildPythonPackage rec {
    name = "twitter.common.collections-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.collections/${name}.tar.gz";
      md5 = "902ebdb7e3daa5d6a5c33f5cc6ea5f8f";
    };

    propagatedBuildInputs = [
      twitter_common_lang
    ];
  };

  twitter_common_http = buildPythonPackage rec {
    name = "twitter.common.http-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.http/${name}.tar.gz";
      md5 = "06fdcb7843f852ecd917fcbab11c2dc4";
    };

    propagatedBuildInputs = [
      twitter_common_log
    ];
  };

  twitter_common_exceptions = buildPythonPackage rec {
    name = "twitter.common.exceptions-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.exceptions/${name}.tar.gz";
      md5 = "08058a8db5f11912b0828d418d7d5113";
    };

    propagatedBuildInputs = [
      twitter_common_lang
      twitter_common_decorators
    ];
  };

  twitter_common_decorators = buildPythonPackage rec {
    name = "twitter.common.decorators-${version}";
    version = "0.3.3";

    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/twitter.common.decorators/${name}.tar.gz";
      md5 = "7de25ff7feef15beec70ef7beb9d2046";
    };
  };
in

stdenv.mkDerivation {
  name = "s3webfront";
  src = ./.;
  buildInputs = [ pythonPackages.wrapPython ];
  pythonPath = with pythonPackages; [
    pythonPackages.boto
    twitter_common_app
    twitter_common_log
    twitter_common_http
    twitter_common_exceptions
  ];

  installPhase = ''
    mkdir -p $out/bin
    install -m 0755 s3webfront.py $out/bin/s3webfront
    wrapPythonPrograms
  '';
}
