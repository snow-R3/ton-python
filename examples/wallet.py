from fift.fift import *


def usage():
    return word(
        'usage',
        string(
            'usage:',
            const('$0'),
            ' <filename-base> <dest-addr> <seqno> <amount> [-B <body-boc>] [-C <transfer-comment>] [<savefile>]'
        ).print(cr=True),
        string(
            'Creates a request to simple wallet created by new-wallet.fif, '
            'with private key loaded from file <filename-base>.pk and address '
            'from <filename-base>.addr, and saves it into <savefile>.boc (\'wallet-query.boc\' by default)'
        ).print(cr=True),
        halt(1)
    )


@script()
def main():
    include('TonUtil.fif')

    usage()


print(main())
