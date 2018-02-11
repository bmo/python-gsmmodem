#!/usr/bin/env python


"""\
Simple script to list SMS messages

@author: Francois Aucamp <francois.aucamp@gmail.com>
"""
from __future__ import print_function
import sys, logging

from gsmmodem.modem import GsmModem, SentSms
from gsmmodem.exceptions import TimeoutException, PinRequiredError, IncorrectPinError


def parseArgs():
    """ Argument parser for Python 2.7 and above """
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Simple script for listing SMS messages')
    parser.add_argument('-i', '--port', metavar='PORT',
                        help='port to which the GSM modem is connected; a number or a device name.')
    #parser.add_argument('-l', '--lock-path', metavar='PATH',
    #                    help='Use oslo.concurrency to prevent concurrent access to modem')
    parser.add_argument('-b', '--baud', metavar='BAUDRATE', default=115200, help='set baud rate')
    parser.add_argument('-p', '--pin', metavar='PIN', default=None, help='SIM card PIN')
    parser.add_argument('-w', '--wait', type=int, default=0, help='Wait for modem to start, in seconds')
    parser.add_argument('-l', '--list', action='store_true', help='List the messages that are available')
    parser.add_argument('-r', '--read', metavar='MSG', default=None, help='Message to read')
    parser.add_argument('-d',  '--delete', metavar='MSG', default=None, help='Message to delete')
    parser.add_argument('--CNMI', default='', help='Set the CNMI of the modem, used for message notifications')
    parser.add_argument('--debug', action='store_true', help='turn on debug (serial port dump)')
    return parser.parse_args()


def parseArgsPy26():
    """ Argument parser for Python 2.6 """
    from gsmtermlib.posoptparse import PosOptionParser, Option
    parser = PosOptionParser(description='Simple script for sending SMS messages')
    parser.add_option('-i', '--port', metavar='PORT',
                      help='port to which the GSM modem is connected; a number or a device name.')
    parser.add_option('-b', '--baud', metavar='BAUDRATE', default=115200, help='set baud rate')
    parser.add_option('-p', '--pin', metavar='PIN', default=None, help='SIM card PIN')
    parser.add_option('-d', '--deliver', action='store_true', help='wait for SMS delivery report')
    parser.add_option('-w', '--wait', type=int, default=0, help='Wait for modem to start, in seconds')
    parser.add_option('-l', '--list', type=int, default=0, help='List the messages that are available')
    parser.add_option('-r', '--read', metavar='MSG', default=None, help='Message to read')
    parser.add_option('-d', '--delete', metavar='MSG', default=None, help='Message to delete')

    parser.add_option('--CNMI', default='', help='Set the CNMI of the modem, used for message notifications')
    parser.add_positional_argument(Option('--destination', metavar='DESTINATION', help='destination mobile number'))
    options, args = parser.parse_args()

    options.message = None
    options.lock_path = None
    print(options)
    return options


def main():
    args = parseArgsPy26() if sys.version_info[0] == 2 and sys.version_info[1] < 7 else parseArgs()
    if args.port == None:
        sys.stderr.write(
            'Error: No port specified. Please specify the port to which the GSM modem is connected using the -i argument.\n')
        sys.exit(1)

    list_sms(args)

def list_sms(args):
    modem = GsmModem(args.port, args.baud, AT_CNMI=args.CNMI)
    if args.debug:
        # enable dump on serial port
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    print('Connecting to GSM modem on {0}...'.format(args.port))
    try:
        modem.connect(args.pin, waitingForModemToStartInSeconds=args.wait)
    except PinRequiredError:
        sys.stderr.write('Error: SIM card PIN required. Please specify a PIN with the -p argument.\n')
        sys.exit(1)
    except IncorrectPinError:
        sys.stderr.write('Error: Incorrect SIM card PIN entered.\n')
        sys.exit(1)
    #print('Checking for network coverage...')
    messages = modem.listStoredSms()
    """
    try:
        modem.waitForNetworkCoverage(5)
    except TimeoutException:
        print('Network signal strength is not sufficient, please adjust modem position/antenna and try again.')
        modem.close()
        sys.exit(1)
    else:
        try:
            pass #sms = modem.sendSms(args.destination, text, waitForDeliveryReport=args.deliver)
        except TimeoutException:
            print('Failed to send message: the send operation timed out')
            modem.close()
            sys.exit(1)
        else:
            modem.close()
    """
    for x in messages:
        print(x.text)

    modem.close()

if __name__ == '__main__':
    main()

