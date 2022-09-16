def add_lsf_coordinator_arguments(parser):
    parser.add_argument('--coordinator-server-port', type=int, default=9002, metavar='N',
                        help='The port of coordinator-server.')
    parser.add_argument('--coordinator-server-ip', type=str, default='localhost', metavar='S',
                        help='The IP of coordinator-server.')
    parser.add_argument('--lsf-job-no', type=str, default='100', metavar='S',
                        help='Job-<ID> assigned by LSF.')
    parser.add_argument('--unique-port', type=str, default='100', metavar='S',
                        help='Which port to use, each client should have different value of this.')
    parser.add_argument('--heartbeats-timelimit', type=float, default=60, metavar='S',
                        help='time to issue heartbeats')
    parser.add_argument('--working-directory', type=str,
                        default='/cluster/scratch/biyuan/fetch_cache', metavar='S',
                        help='The IP of coordinator-server.')

def add_global_coordinator_arguments(parser):
    parser.add_argument('--db-server-address', type=str,
                        default="http://xzyao:agway-fondly-ell-hammer-flattered-coconut@db.yao.sh:5984/", metavar='N',
                        help='Key value store address.')

def print_arguments(args):
    args_dict = vars(args)
    print("======================Input Arguments=========================")
    for key in args_dict.keys():
        print(key, ": ", args_dict[key])
    print("==============================================================")