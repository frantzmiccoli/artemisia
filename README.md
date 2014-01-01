What's Artemisia for?
=====================

I had some common data visualisation use cases that includes:

* Loading data from CSV files (usually one file per record)
* Removing some lines (filtering), to refine some display for example or remove extreme value
* Select only one single line (usually the last one) of my CSV files: when measuring a phenomenon, sometimes only the last stage is interesting.
* Modify the data on the fly, to normalize some data or combine them into other fields.
* Generate a basic scatter plot or bar chart from the data.


This is what Artemisia is doing with Python 2.7.

How to install it
=================

Requirements
------------

You need:
  * scikit-learn
  * pandas
  * statsmodel
  * matplotlib
  * scipy
  * numpy
  * patsy
  * husl
  * moss
  * seaborn
  
Use Vagrant
-----------

It can be boring to setup everything, that's why a Vagrantfile configuration is available.

  * Install Vagrant
  * Go into the clone of this repo
  * `vagrant up`
  * `vagrant ssh` (this will connect you inside the VM)
  * `cd /vagrant` (this will put you inside the directory of the project with everything you need already installed)


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

As a lib
========

Open artemisia.py and look at the method called `run()`, it's the most important one, where all the logic is.

You can copy this basic structure and try to tweak things to have a more custom behavior if you need it.

Give me more details
====================
This sections mainly covers built in modifiers that can be useful.

Normalizing your data
---------------------
If you do just want to normalize a field, just use `normalized_original_field_name`.

For **more advanced usage**, you may need to perform your normalization after a presplitting of your instance.

**For example**, it may not make sense to normalize of performance for different problems by mixing every single data. Then you'll need to update your loader.


    import artemisia.registry as aregistry
    def get_normalized_performance_modifier():
        data_dir_path = aregistry.instance.get_data_dir_path()
        
        # We normalize considering different split of our data according to fixed 
        # fields whose value shouldn't change within a split 
        fixed_fields = ['problem_type']
        normalizer = gnormalizer.Normalizer(data_dir_path, 'performance',
                                        fixed_fields=fixed_fields)
                                        
        # Bonus point we only take the last point of each file because
        # it makes sense for our given problem 
        normalizer.filter_manager.add_first_to_match_filter('last')

        def normalized_performance_modifier(value_point):
            value_point = normalizer.normalize(value_point)
            return value_point

        return normalized_performance_modifier


Clusters pseudofields
---------------------

Clusters pseudofield can be computed and used on the fly.

**For example** if your data are containing temperature and humidity in many rooms, you may would like to run artemisia only for a subset of `rooms`, let's say two thirds of them. You then just have to add a filter like:

    -f "cluster_room_3 in 0 1"
    
**With more details**, this will compute a hash as an int from each `room` and fill a `cluster_room_3` with the modulo 3 of this int (which should randomly sample the rooms). Then the filter just simply extract the line for which the value is either 0 or 1.

If don't want to sample accross a given field but just over the lines: you can also use things like `cluster_3`.


What's missing?
===============

* Artemisia is not clean, some refactoring my be required, especially in the view component
* Artemisia let users do a great deal of preprocessing before display, it would be a neat feature to also let users export their data to some exchange format (CSV, ARFF)


License
=======

Copyright 2013 Fräntz Miccoli

Released under the MIT License.
