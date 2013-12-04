What's Artemisia for?
=====================

I had some common data visualisation use cases that includes:

* Loading data from CSV files (usually one file per record)
* Removing some lines (filtering), to refine some display for example or remove extreme value
* Select only on line (usually the last one) of my CSV files: when measuring a phenomenon, sometimes only the last stage is interesting.
* Modify the data on the fly, to normalize some data or combine them into other fields.
* Generate a basic scatter plot or bar chart from the data.


This is what Artemisia is doing with Python 2.7.

How can I use it?
=================

As a command
------------

Example: `python /path/to/artemisia.py -l yourproject.loader  -i ../../simulations/output -x problem_kind -y "COUNT(*)" -m last -f "problem_type not in trivial_problem_1 trivial_problem_2"`

    Artemisia tool is meant to parse data in CSV to build graph after some basic preprocessing

    optional arguments:
      -h, --help  show this help message and exit
      -x X        The data field to use for the x side of the plot
      -y Y        The data field to use for the y side of the plot
      -c COLOR    The data field to use for coloring elements of the plot
      -m MATCHES  Consider the first element of a simulation data that match this
                  filter
      -f FILTERS  Consider only elements that match this filter
      -l LOADER   A python package to use as loader
      -s          Flag to force scatter plot
      -i INPUT    The input dir to consider (mandatory)
      -o OUTPUT   The output file to use

If you provide a **loader package** it will:

* Be included before running any data loading (you can use it to change the data loader casting for example)

        import artemisia.dataloader as adataloader

        adataloader.DataLoader.add_cast(['best_fitness', 'pick_reason',
                                     'average_fitness', 'clustering_coefficient'],
                                    'float')
        adataloader.DataLoader.add_cast(['pick_proportion', 'replace_proportion',
                                     'mutation_rate', 'migration_rate'],
                                    'percentage')
        adataloader.DataLoader.add_cast(['evaluations', 'population_size',
                                     'populations_count', 'diameter'],
                                    'int')


* Be used to look for function called get_field_name_modifier, this function must return a function taking a dictionnary as input (the line of your CSV) and returning another dictionnary (it's supposed to add a field name `field_name`)

        def get_version_number_modifier():
            def system_number_modifier(value_point):
                system = value_point['system']
                split_system = system.split('-')
                if len(split_system) == 2:
                    version_number = int(split_system[-1])
                else:
                    version_number = 0
                value_point['version_number'] = version_number
                return value_point
            return system_number_modifier
            

Some notes about **filters**:

* They support different operators like 'in', 'not in', basic comparison operator like '=', '<=' and others alike.
* They MUST be used with one field name on the left side
* They MUST be used with a space separating every element `price < 10` works, `price<10` won't since spaces are used to parse those filters.

About **matches**:
* They support the exact same thing as filters
* There's a special case for the match with is the `last` value which just take the last value of a file



What's missing?
===============

1. Artemisia is not clean, some refactoring my be required, especially in the view component
2. There's no standardized way to normalize data or at least to factorize code around that given need… Those are missing.

License
=======

Copyright 2013 Fräntz Miccoli

Released under the MIT License.