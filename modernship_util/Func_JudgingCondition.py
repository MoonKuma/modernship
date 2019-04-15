def judgingconditon(input_dict):
    if input_dict.has_key("date_list"):
        mindate = min(input_dict["date_list"])
        maxdate = max(input_dict["date_list"])
        strdate = ' where date between \"' + mindate + '\" and \"' + maxdate + '\" '
        if input_dict.has_key("channel_list"):
            strchannel = ' and channel in ('
            for i in input_dict["channel_list"]:
                if (index[i] < len(input_dict["channel_list"] - 1)):
                    strchannel += str(i) + ","
                else:
                    strchannel += str(i) + ") "
        else:
            strchannel = ''
        if input_dict.has_key("zone_list"):
            strzone = ' and zoneid in ('
            for i in input_dict["zone_list"]:
                if (index[i] < len(input_dict["zone_list"] - 1)):
                    strzone += str(i) + ","
                else:
                    strzone += str(i) + ") "
        else:
            strzone = ''
    else:
        strdate = ''
        if input_dict.has_key("channel_list"):
            strchannel = ' where channel in ('
            for i in input_dict["channel_list"]:
                if (index[i] < len(input_dict["channel_list"] - 1)):
                    strchannel += str(i) + ","
                else:
                    strchannel += str(i) + ") "
            if input_dict.has_key("zone_list"):
                strzone = 'and zoneid in ('
                for i in input_dict["zone_list"]:
                    if (index[i] < len(input_dict["zone_list"] - 1)):
                        strzone += str(i) + ","
                    else:
                        strzone += str(i) + ") "
            else:
                strzone = ''
        else:
            strchannel = ''
            if input_dict.has_key("zone_list"):
                strzone = ' where zoneid in ('
                for i in input_dict["zone_list"]:
                    if (index[i] < len(input_dict["zone_list"] - 1)):
                        strzone += str(i) + ","
                    else:
                        strzone += str(i) + ") "
            else:
                strzone = ''

    return [strdate,strchannel,strzone]