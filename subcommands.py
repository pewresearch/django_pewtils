import sys, datetime, traceback, copy

from optparse import NO_DEFAULT, OptionParser
from importlib import import_module

from django.conf import settings
from django.core.management.base import CommandError, BaseCommand, handle_default_options


class SubcommandDispatcher(BaseCommand):

    """
    A wrapper for subcommands; looks in the subcommand directory for a folder and file based on the passed parameters.
    Modified by borrowed from Django Subcommander repository.
    """

    help = "A wrapper for subcommands"

    subcommands = []
    custom_commander = None

    import_template = '{app_name}.management.subcommands.{dispatcher_name}.{module_name}'

    def __init__(self):
        self.app_name = settings.SITE_NAME
        super(SubcommandDispatcher, self).__init__()

    def print_subcommands(self, prog_name):
        usage = ['', 'Available subcommands:']
        for name in sorted(self.subcommands):
            usage.append('  {0}'.format(name))
        return '\n'.join(usage)

    def usage(self, subcommand):
        usage = '%prog {0} subcommand [options] [args]'.format(subcommand)
        if self.help:
            return '{0}\n\n{1}'.format(usage, self.help)
        return usage

    def print_help(self, prog_name, subcommand):
        super(SubcommandDispatcher, self).print_help(prog_name, subcommand)
        sys.stdout.write('{0}\n\n'.format(self.print_subcommands(prog_name)))

    def get_subcommand(self, dispatcher, subcommand):

        if self.custom_commander:
            return self.custom_commander(subcommand)
        else:
            try:
                module = import_module(self.import_template.format(
                    app_name=self.app_name,
                    dispatcher_name=dispatcher,
                    module_name=subcommand)
                )
                return module.Command()
            except KeyError:
                raise CommandError('Unknown subcommand: {0} {1}'.format(self.app_name, subcommand))

    def run_from_argv(self, argv):

        # Set up any environment changes requested (e.g., Python path and Django settings), then run this command.
        if len(argv) > 2 and not argv[2].startswith('-') and argv[2] in self.subcommands:
            dispatcher = argv[1]
            subcommand = argv[2]
            klass = self.get_subcommand(dispatcher, subcommand)
            klass.run_from_argv(argv[1:])
        else:
            super(SubcommandDispatcher, self).run_from_argv(argv)

            # if len(argv) > 2 and not argv[2].startswith('-') and argv[2] in self.subcommands:
            #     subcommand = argv[2]
            #     klass = self.get_subcommand(subcommand)
            #     parser = OptionParser(prog=argv[0], usage=klass.usage('{0} {1}'.format(argv[1], subcommand)),
            #         version=klass.get_version(), option_list=klass.option_list)
            #     klass.add_arguments(parser)
            #     options, args = parser.parse_args(argv[3:])
            #     args = [subcommand] + args
            # else:
            #     parser = OptionParser(prog=argv[0], usage="", version=self.get_version(), option_list=self.option_list)
            #     options, args = parser.parse_args(argv[2:])
            #
            # for attr in ["settings", "pythonpath"]:
            #     if not hasattr(options, attr):
            #         setattr(options, attr, None)
            #
            # handle_default_options(options)
            # print options.__dict__
            # print args
            # self.execute(*args, **options.__dict__)

    def handle(self, *args, **options):
        if not args or args[0] not in self.subcommands:
            return self.print_help('./manage.py', self.app_name)
        subcommand, args = args[0], args[1:]

        klass = self.get_subcommand(subcommand)
        # Grab out a list of defaults from the options. optparse does this for
        # us when the script runs from the command line, but since
        # call_command can be called programatically, we need to simulate the
        # loading and handling of defaults (see #10080 for details).
        defaults = {}
        for opt in klass.option_list:
            if opt.default is NO_DEFAULT:
                defaults[opt.dest] = None
            else:
                defaults[opt.dest] = opt.default
        defaults.update(options)

        return klass.execute(*args, **defaults)


        # def handle_logger(handle):
        #     def wrapper(self, *args, **options):
        #         #if ENV == "prod":
        #         save_args = self.__module__.split('.')[-2:] + list(args[1:])
        #         command = " ".join(save_args)
        #         opts = dict(options)
        #         if "settings" in opts: del opts["settings"]
        #         if "verbosity" in opts: del opts["verbosity"]
        #         if "pythonpath" in opts: del opts["pythonpath"]
        #         if "traceback" in opts: del opts["traceback"]
        #         if "no_color" in opts: del opts["no_color"]
        #         for opt in opts:
        #             if opts[opt] not in [True, False]: command += " --%s %s" % (opt, str(opts[opt]))
        #         for opt in opts:
        #             if opts[opt] == True: command += " --%s" % opt
        #         log = CommandLog.objects.create(args=command, options=options)
        #         try:
        #             handle(self, *args, **options)
        #             log.end_time = datetime.datetime.now()
        #             log.save()
        #         except Exception as e:
        #             log.error = {
        #                 "traceback": traceback.format_exc(),
        #                 "exception": e
        #             }
        #             log.save()
        #             raise e
        #         # else:
        #         #     handle(self, *args, **options)
        #     return wrapper