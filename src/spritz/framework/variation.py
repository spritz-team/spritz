from copy import deepcopy
from functools import wraps
from typing import NewType
import awkward as ak

columnType = NewType("columnType", str | tuple[str] | tuple[str, str])
columnType = str | tuple[str] | tuple[str, str]


class Variation:
    """
    Variation helps registering variations for columns and query them

    Every column can be represented by a str or tuple

    Every variation must have a unique name (e.g. ``JES_up``)
    """

    def __init__(self):
        # variations_dict for each variation will save a list of substitutions to perform
        # each substitution is registered as a tuple (nominal_column, varied_column)
        self.variations_dict = {}
        # columns_dict for each column will save a list of all variations that affect such column
        self.columns_dict = {}

    @staticmethod
    def format_varied_column(column: columnType, variation_name: str):
        if isinstance(column, str):
            return f"{column}_{variation_name}"
        elif isinstance(column, tuple):
            _list = list(column[:-1])
            _list.append(f"{column[-1]}_{variation_name}")
            return tuple(_list)
        else:
            print(
                "Cannot format varied column", column, "for variation", variation_name
            )
            raise Exception

    def register_variation(
        self,
        columns: list[columnType],
        variation_name: str,
        format_rule=format_varied_column,
    ):
        """
        Register a new variation with name ``variation_name`` for the ``columns`` provided.
        Only used when a new variations has to be created.

        Parameters
        ----------
        columns : list[columnType]
            _description_
        variation_name : str
            _description_
        """
        self.variations_dict[variation_name] = []
        self.add_columns_for_variation(variation_name, columns, format_rule=format_rule)

    def add_columns_for_variation(
        self,
        variation_name: str,
        columns: list[columnType],
        format_rule=format_varied_column,
    ):
        """
        Adds the columns to the list of columns for the provided variation

        Only used when a variation has already been created.

        Parameters
        ----------
        variation_name : _type_
            _description_
        columns : _type_
            _description_

        Raises
        ------
        Exception
            _description_
        """
        if variation_name not in self.variations_dict:
            # raise Exception(f"Variation '{variation_name}' not yet defined")
            self.register_variation(columns, variation_name, format_rule)
            return
        for column in columns:
            self.variations_dict[variation_name].append(
                (
                    column,
                    format_rule(column, variation_name),
                )
            )
            variation_list = self.columns_dict.get(column, [])
            variation_list.append(variation_name)
            self.columns_dict[column] = variation_list

    def get_variation_columns(self):
        """
        Returns all columns that are storing varied quantities, aka varied branches
        """
        columns = []
        for variation in self.variations_dict:
            for switch in self.variations_dict[variation]:
                columns += [switch[1]]
        return columns

    def get_variations_for_column(self, column):
        """
        Returns all the variations for a column

        Parameters
        ----------
        column : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return self.columns_dict[column]

    def get_variations_all(self):
        """
        Returns the list of variation names that are registerd

        Returns
        -------
        _type_
            _description_
        """
        return list(self.variations_dict.keys())

    def get_variation_subs(self, variation_name):
        return self.variations_dict[variation_name]

    def get_variations_affecting(self, columns: type[str | list[str]] = "all"):
        """
        Returns the list of variations that affect the provided columns

        Parameters
        ----------
        columns : _type_
            _description_
        """
        variations = []

        if columns == "all":
            return list(self.variations_dict.keys())
        if isinstance(columns, str):
            raise Exception(
                'columns in get_variations_affecting can only be the special str "all" or a list of string'
            )

        for column in columns:
            variations += self.columns_dict.get(column, [])
        return list(set(variations))


def get_columns(events):
    columns = []
    for column_base in ak.fields(events):
        column_suffixes = ak.fields(events[column_base])
        if len(column_suffixes) == 0:
            columns.append((column_base,))
        else:
            for column_suffix in column_suffixes:
                columns.append((column_base, column_suffix))
    return columns


def vary(reads_columns: type[str | tuple[str]] = "all"):
    def actual_wrapper(func: callable):
        @wraps(func)
        def wrapper_decorator(
            events: ak.Array,
            variations: Variation,
            *args,
            doVariations: bool = False,
            **kwargs,
        ):
            # print(events)
            # print(variations)
            # print(*args)
            if doVariations:
                # since func will create varied columns, just run on nominal
                return func(
                    events, variations, *args, doVariations=doVariations, **kwargs
                )
                # return events, variations
            else:
                # Make a backup copy for events
                originalEvents = ak.copy(events)

                # Save all current variations, will loop over them callind the function

                original_fields = get_columns(events)
                # print(original_fields)

                # Run the nominal
                new_events, _ = func(
                    events, variations, *args, doVariations=doVariations, **kwargs
                )
                new_variations = deepcopy(variations)

                nom_fields = get_columns(new_events)
                # print(nom_fields)
                new_fields = list(set(nom_fields).difference(original_fields))
                # print(new_fields)
                # print(variations.get_variations_affecting(reads_columns))
                for variation in variations.get_variations_affecting(reads_columns):
                    events = ak.copy(originalEvents)

                    for switch in variations.variations_dict[variation]:
                        if len(switch) == 2:
                            # print(switch)
                            variation_dest, variation_source = switch
                            events[variation_dest] = events[variation_source]

                    varied_events, _ = func(
                        events, variations, *args, doVariations=doVariations, **kwargs
                    )

                    # copy all the varied columns here
                    for new_field in new_fields:
                        varied_field = Variation.format_varied_column(
                            new_field, variation
                        )
                        # print(
                        #     "registering new field",
                        #     new_field,
                        #     "with varied name",
                        #     varied_field,
                        # )
                        new_events[varied_field] = ak.copy(varied_events[new_field])
                    # and register them
                    new_variations.add_columns_for_variation(variation, new_fields)

                return new_events, new_variations

        return wrapper_decorator

    return actual_wrapper
