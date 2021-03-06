#!/usr/share/clearwater/clearwater-prov-tools/env/bin/python

# @file update_user.py
#
# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

import sys
import logging
import argparse
from metaswitch.ellis import settings
from metaswitch.ellis.prov_tools import utils

_log = logging.getLogger();

def main():
    parser = argparse.ArgumentParser(description="Update user")
    parser.add_argument("-k", "--keep-going", action="store_true", dest="keep_going", help="keep going on errors")
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", help="don't display the user")
    parser.add_argument("--hsprov", metavar="IP:PORT", action="store", help="IP address and port of homestead-prov")
    parser.add_argument("--plaintext", action="store_true", help="store password in plaintext")
    parser.add_argument("--ifc", metavar="iFC-FILE", action="store", dest="ifc_file", help="XML file containing the iFC (default: iFC unchanged)")
    parser.add_argument("--prefix", action="store", default="123", dest="twin_prefix", help="twin-prefix (default: 123)")
    parser.add_argument("--impi", action="store", default="", dest="impi", help="IMPI (default: derived from the IMPU)")
    parser.add_argument("dns", metavar="<directory-number>[..<directory-number>]")
    parser.add_argument("domain", metavar="<domain>")
    parser.add_argument("--password", help="new password (default: password unchanged)")
    args = parser.parse_args()

    utils.setup_logging()
    settings.HOMESTEAD_URL = args.hsprov or settings.HOMESTEAD_URL

    ifc = None
    if args.ifc_file:
        ifc = utils.build_ifc(args.ifc_file, args.domain, args.twin_prefix)
        if not ifc:
            sys.exit(1)

    if not utils.check_connection():
        sys.exit(1)

    success = True
    for dn in utils.parse_dn_ranges(args.dns):
        public_id = "sip:%s@%s" % (dn, args.domain)
        private_id = "%s@%s" % (dn, args.domain)

        if args.impi != "":
            private_id = args.impi

        if utils.update_user(private_id, public_id, args.domain, args.password, ifc, args.plaintext):
            if not args.quiet and not utils.display_user(public_id):
                success = False
        else:
            success = False

        if not success and not args.keep_going:
            break

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
