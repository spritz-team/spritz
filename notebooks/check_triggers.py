import json

from data.common.TrigMaker_cfg import Trigger
from spritz.framework.framework import add_dict_iterable


# def add_dict_iterable()
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


for era in ["Full2016v9HIPM", "Full2016v9noHIPM", "Full2017v9", "Full2018v9"]:
    print("\n\n", era)
    triggers = [k["DATA"] for k in Trigger[era].values()]
    for _era in range(len(triggers)):
        print(_era)
        for trigger in triggers[_era]:
            triggers[_era][trigger] = set(triggers[_era][trigger])

    # def difference(list_of_d):
    #     diff = {}
    #     for d1 in list_of_d:
    #         for key in d1:
    #             if key not in d2:
    #                 diff[key] = d1[key]
    #             else:
    #                 diff[key] = set(d1[key]) ^ set(d2[key])
    #     for key in d2:
    #         if key in diff:
    #             continue
    #         if key not in d2:
    #             diff[key] = d2[key]
    #         else:
    #             diff[key] = set(d1[key]) ^ set(d2[key])
    #     return diff
    # add

    # print(difference(triggers[0], triggers[1]))

    print(json.dumps(add_dict_iterable(triggers), indent=2, cls=NumpyEncoder))
    print([j for k in add_dict_iterable(triggers).values() for j in k])
