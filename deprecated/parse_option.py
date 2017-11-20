from optparse import OptionParser

version_info = (0, 3, 0)
version_str = "version: {}".format(".".join([str(_) for _ in version_info]))


def parse_option():
    parser = OptionParser(version=version_str)
    return parser.parse_args()


if __name__ == '__main__':
    options, args = parse_option()

