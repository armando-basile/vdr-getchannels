#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__     = "Armando Basile"
__copyright__  = "Copyright 2011-2015"
__credits__    = ["Mona66, KingOfSat"]
__license__    = "GPL"
__version__    = "0.7.0"
__daterel__    = "2015-03-02"
__maintainer__ = "Armando Basile"
__email__      = "hmandevteam@gmail.com"



#import sys
import urllib
import string

import os.path
import argparse
from app_params import app_params




# main class to manage channels list generation
class getchannels:
    
    # Attributes
    
    
    # class constructor
    def __init__(self):

        # local attributes
        self.__outputList = list()
        self.__outputListLower = list()
        self.__transponder_list = list()
        self.__channels_bouquets  = list()
        self.__name_bouquets      = list()    
        
        # check command line arguments before start
        self.__parse_args()

        # check if is present config file        
        if self.__args.configfile != None:
            # check for config file presence
        
            if os.path.exists('./conf/' + self.__args.configfile) == False:
                # file not founded                
                print 'specified config file not founded \n' + os.path.abspath('./conf/' + self.__args.configfile) + \
                      '\nplease check it and retry'
                exit(1)
            
            # process config file
            self.__parse_config_file()


        # process html code from kingofsat website
        self.__parse_kingofsat_list()
        
        # write output
        self.__write_output_file()
        
        return





    # check for command line arguments
    def __parse_args(self):
        
        # create parser for command line parameters
        parser = argparse.ArgumentParser(description='Generate channels list for VDR.')
        
        parser.add_argument('-u', '--upper', help='set to upper polarity digit in output', 
                            action="store_true", dest='upper', default=False)

        parser.add_argument('-c', '--useconfig', type=str, metavar='FILENAME', dest='configfile', default=None,
                            help='enable use of config file, searched in "conf" subfolder, to generate output')
        
        parser.add_argument('-l', '--list', type=str, metavar='LIST_ID', required=True,
                            dest='list_id', choices=app_params.sat_list.keys(),
                            help='''set KingOfSat source channels list used to generate local VDR channels list.
                                    Can use one of follow values: ''' + ", ".join(app_params.sat_list.keys()))
                                    
        parser.add_argument('-o', '--output', type=str, metavar='FILENAME', dest='outfile', required=True,
                            help='enable use of config file, searched in "conf" subfolder, to generate output')

        # assign command line parse output to class attribute
        self.__args = parser.parse_args()        
        return







    # read config file
    def __parse_config_file(self):
        # update local var with config file content
        file = open('./conf/' + self.__args.configfile, "r")
        cfgFile = file.read()
        file.close()
        
        # generate list with config file rows
        rows = cfgFile.split("\n")
        
        # loop for all rows in config file
        for row in rows:
            row = row.strip()
            # remove empty rows
            if len(row) > 0:
                # remove comments
                if row[0:1] != "#":                    
                    # update local vars with file content
                    self.__outputList.append(row)
                    self.__outputListLower.append(row.replace(" ", "").lower())

        





    # get html code from kingofsat using specified url and extract data
    def __parse_kingofsat_list(self):
        
        # get html
        f = urllib.urlopen(app_params.sat_list[self.__args.list_id])
        web_content = f.read()
        f.close()
        
        # split webpage content in many trasponder sections
        self.__transponder_list = web_content.split('''color="yellow">''' + app_params.sat_id[self.__args.list_id])
        
        # parse all transponder section founded
        for idx in range(1, len(self.__transponder_list)):            
            self.__parse_transponder(self.__transponder_list[idx])
            







    # parse single transponder
    def __parse_transponder(self, trans_code):
        
        # offsets
        tra1=0
        tra2=0
        tmp=0
        
        # search initial transponder data
        tra1= string.find(trans_code, '''<td width="5%" class="bld">''')
        tmp = string.find(trans_code, '''<td width="5%" class="nbld">''')
        
        # check for second possible tag
        if tmp > 0 and tmp < tra1:
            tra1 = tmp+1
        
        # transponder frequency
        tra2= string.find(trans_code, ".", tra1+27)
        freq = trans_code[tra1+27:tra2]
        
        # polarity
        tra1 = string.find(trans_code, '''class="bld">''', tra2+1)        
        tmp = string.find(trans_code, '''class="nbld">''', tra2+1)   
        if tmp > 0 and tmp < tra1:
            tra1 = tmp+1
    
        tra2 = string.find(trans_code, "</td>", tra1+12)
        polar = trans_code[tra1+12:tra2]
        
        # check for polar digit representation
        if self.__args.upper == True:
            polar = polar.upper()
        else:
            polar = polar.lower()
    
        # dvb
        tra1 = string.find(trans_code, "DVB-", tra2+1)        
        tra2 = string.find(trans_code, "</td>", tra1+4)
        dvb = trans_code[tra1+4:tra2]
    
        # modular
        tra1 = string.find(trans_code, '''">''', tra2+1)        
        tra2 = string.find(trans_code, "</td>", tra1+2)
        modular = trans_code[tra1+2:tra2]

        # symbol rate
        tra1 = string.find(trans_code, '''class="bld">''', tra2+1)        
        tmp = string.find(trans_code, '''class="nbld">''', tra2+1)   
        if tmp > 0 and tmp < tra1:
            tra1 = tmp+1
    
        tra2 = string.find(trans_code, "</a>", tra1+12)
        sr = trans_code[tra1+12:tra2]
    
        # fec
        tra1 = string.find(trans_code, '''class="bld">''', tra2+1)        
        tmp = string.find(trans_code, '''class="nbld">''', tra2+1)   
        if tmp > 0 and tmp < tra1:
            tra1 = tmp+1
    
        tra2 = string.find(trans_code, "</a>", tra1+12)
        fec = trans_code[tra1+12:tra2]
    
        # network id
        tra1 = string.find(trans_code, "NID:", tra2+1)        
        tra2 = string.find(trans_code, "</td>", tra1+4)
        nid = trans_code[tra1+4:tra2]
        nid = nid.replace('''<a class="n">''', "")
        nid = nid.replace("</a>", "").strip()
    
        # transponder id
        tra1 = string.find(trans_code, "TID:", tra2+1)        
        tra2 = string.find(trans_code, "</td>", tra1+4)
        tid = trans_code[tra1+4:tra2]
        tid = tid.replace('''<a class="n">''', "")
        tid = tid.replace("</a>", "").strip()
    
    
        # check for dvb-s type
        if dvb == "S2":
            # update row and video pid with dvb-s2 parameters
            trparam  = "M5O35S1"
            vpidtype = "=27"
        else:
            # update row and video pid with dvb-s parameters
            trparam  = "M2S0"
            vpidtype = "=2"
                
        # create row template
        tmpRow = "<chname>;" + \
                 "<bouquet>:" + \
                 freq + ":" + \
                 polar + "C" + fec.replace("/","") + trparam + ":" + \
                 "S" +  self.__args.list_id + ":" + \
                 sr + ":" + \
                 "<vpid>" + vpidtype + ":" + \
                 "<apid>:" + \
                 "<subtxt>:" + \
                 "<caid>:" + \
                 "<sid>:" + \
                 nid + ":" + \
                 tid + \
                 ":0"
        
        # split remaining data in many channel sections
        tmpCh = trans_code[tra2+4:]
        tmpChCodes = tmpCh.split(''' title="Id: ''')
        
        # parse all channel section founded
        for idx in range(1, len(tmpChCodes)):
            tmpChList = self.__parse_channel(tmpChCodes[idx])
    
            # update templare row with returned values chName, bqt, sid, vpid, apid, subtxt
            for chInfos in tmpChList:
                chRow = tmpRow.replace("<chname>", chInfos[0])
                chRow = chRow.replace("<bouquet>", chInfos[1])
                chRow = chRow.replace("<sid>", chInfos[2])
                chRow = chRow.replace("<vpid>", chInfos[3])
                chRow = chRow.replace("<apid>", chInfos[4])
                chRow = chRow.replace("<subtxt>", chInfos[5])
                
                # check for caid value for this bouquet
                if app_params.caid_bouquets.has_key(chInfos[1]):
                    # know value
                    chRow = chRow.replace("<caid>", app_params.caid_bouquets[chInfos[1]])
                else:
                    # unknow value, set to '0'
                    chRow = chRow.replace("<caid>", "0")
                
                # check for config file usage
                if self.__args.configfile != None:
                    # try to found channel in our preset list from config file
                    try:
                        cfIdx = self.__outputListLower.index((chInfos[0] + ";" + chInfos[1]).replace(" ", "").lower())
                    except ValueError:
                        cfIdx = -1
        
                    # if founded channel, update row
                    if cfIdx >= 0:
                        # update row for channels in config file
                        self.__outputList[cfIdx] = chRow
        
                else:       
                    # update total list
                    try:
                        # get already added channel position
                        ib = self.__name_bouquets.index(chInfos[1])                    
                    except ValueError:
                        # added new position for channel
                        self.__name_bouquets.append(chInfos[1])
                        self.__channels_bouquets.append("")
                        ib = len(self.__name_bouquets)-1
                    
                    # update value
                    self.__channels_bouquets[ib] += chRow + "\n"

        
        
        
        
        
        

    
    # parse channel section
    def __parse_channel(self, channel_str):
        
        # offsets
        tra1=0
        tra2=0        
        out_channel_list = list()
    
        # channel name
        tra2 = string.find(channel_str, "\"")
        chName = channel_str[tra1:tra2]
        
        # bouquets
        tra1 = string.find(channel_str, "<TD ", tra2+1)
        tra1 = string.find(channel_str, "<TD ", tra1+10)
        tra1 = string.find(channel_str, "<TD ", tra1+10)
        tra2 = string.find(channel_str, "</TD>", tra1+10)
        bqtStr = channel_str[tra1+10:tra2]
        bouquetList = self.__parse_bouquet(bqtStr)
        
        # service id
        tra1 = string.find(channel_str, "<TD ", tra2+3)
        tra1 = string.find(channel_str, "<TD ", tra1+10)
        tra1 = string.find(channel_str, ">", tra1+10)    
        tra2 = string.find(channel_str, "<", tra1+1)
        sid = channel_str[tra1+1:tra2].strip()
        
        # video pid
        tra1 = string.find(channel_str, "<TD ", tra2+1)
        tra1 = string.find(channel_str, ">", tra1+10)    
        tra2 = string.find(channel_str, "<", tra1+1)
        vpid = channel_str[tra1+1:tra2].strip()
    
        # audio pid
        tra1 = string.find(channel_str, "<TD ", tra2+1)
        tra1 = string.find(channel_str, ">", tra1+10)    
        tra2 = string.find(channel_str, "</TD>", tra1+1)
        apidStr = channel_str[tra1:tra2].strip()
        apid = self.__parse_audio_pid(apidStr)
        
        # pcr
        tra1 = string.find(channel_str, "<TD ", tra2+1)
        tra1 = string.find(channel_str, "<TD ", tra1+10)
        tra1 = string.find(channel_str, ">", tra1+10)    
        tra2 = string.find(channel_str, "<", tra1+1)
        pcr = channel_str[tra1+1:tra2].strip().replace("&nbsp;", "")
        
        # update video pid with pcr parameter if required
        if (pcr != vpid):
            vpid += "+" + pcr
    
        # Subtitles
        tra1 = string.find(channel_str, "<TD ", tra2+1)
        tra1 = string.find(channel_str, ">", tra1+10)    
        tra2 = string.find(channel_str, "<", tra1+1)
        subtxt = channel_str[tra1+1:tra2].strip().replace("&nbsp;", "")
        
        if subtxt == "":
            subtxt = "0"
        
        
        # fill channels output list
        for bqt in bouquetList:
            out_channel_list.append([chName, bqt, sid, vpid, apid, subtxt])
    
        return out_channel_list
    

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

    
    # parse audio pid string
    def __parse_audio_pid(self, strPid):
        
        outAudioPid=""
        pidstop = 0
        tmpapid = ""
        tmpretapid = ""
        outDolbyPids = ""
        outOtherPids = ""
        dolbyPids = list()
        otherPids = list()    
    
        
        # generate array of all audio pids sections
        audiopids = strPid.split("<br")
        
        # loop for each audio pid
        for audiopid in audiopids:
            # process audio pid section     
            pidstart = string.find(audiopid, ">")
            pidstop  = string.find(audiopid, "<", pidstart+1)
            
            # check for characters next pid
            if pidstop < 0:
                # there is only audio pid in string section
                tmpapid=audiopid[pidstart+1:].replace("&nbsp;", "").strip()
            else:
                # there are other info in audio pid string
                tmpapid=audiopid[pidstart+1:pidstop].replace("&nbsp;", "").strip()
            
            # remove unused characters
            tmpapid = tmpapid.split(" ")[0]
            
            # retrieve other audio pid info from remaining characters
            tmpretapid = tmpapid + "=" + self.__parse_audio_pid_single(audiopid[pidstop:])
            
            # check for audio pid type
            if (tmpretapid.find("@106") > 0):
                # dolby digital audio pid
                dolbyPids.append(tmpretapid)
            else:
                # other audio pid
                otherPids.append(tmpretapid)
            
            #tmpapid+="=" + ParseAudioPidSingle(audiopid[pidstop:]) + ","
            
            # update audio pids output string
            #outAudioPid+=tmpapid
        
        # check for non dolby audio pid presence
        if (len(otherPids) > 0):
            # loop for each non dolby audio pid
            for itemPid in otherPids:
                outOtherPids += itemPid + ","
            
            # remove latest comma
            outOtherPids = outOtherPids[0:len(outOtherPids)-1]
        
        else:
            # no other audio pid presents        
            outOtherPids = "0"
    
    
        # check for dolby audio pid presence
        if (len(dolbyPids) > 0):
            # loop for each dolby audio pid
            for itemPid in dolbyPids:
                outDolbyPids += itemPid + ","
            
            # remove latest comma
            outDolbyPids = outDolbyPids[0:len(outDolbyPids)-1]
        
        else:
            # no dolby audio pid presents
            outDolbyPids = ""
        
        
        # check for dolby pid presence
        if (outDolbyPids == ""):
            # output string contains only non dolby pids
            outAudioPid = outOtherPids
        else:
            # output string contains non dolby pids + ';' + dolby pids
            outAudioPid = str(outOtherPids) + ";" + outDolbyPids
        
        
        return outAudioPid
    
            
            
        
        
        
        
            
    
    # extract audio pid info from each audio pid
    def __parse_audio_pid_single(self, strInfo):
        outinfo = ""
        
        # parse audio type
        if string.find(strInfo, '''title="AC3''') > 0:
            outinfo = "@106"
        else:
            outinfo = "@4"
        
        
        # parse language name
        if string.find(strInfo, '''title="Italiano''') > 0:
            outinfo = "ita" + outinfo
        elif string.find(strInfo, '''title="Inglese''') > 0:
            outinfo = "eng" + outinfo
        elif string.find(strInfo, '''title="Polacco''') > 0:
            outinfo = "pol" + outinfo
        elif string.find(strInfo, '''title="Romeno''') > 0:
            outinfo = "rom" + outinfo
        elif string.find(strInfo, '''title="Farsi''') > 0:
            outinfo = "far" + outinfo
        elif string.find(strInfo, '''title="Portoghese''') > 0:
            outinfo = "por" + outinfo
        elif string.find(strInfo, '''title="Urdu''') > 0:
            outinfo = "urd" + outinfo
        elif string.find(strInfo, '''title="Francese''') > 0:
            outinfo = "fra" + outinfo
        elif string.find(strInfo, '''title="Tedesco''') > 0:
            outinfo = "ger" + outinfo
        elif string.find(strInfo, '''title="Arabo''') > 0:
            outinfo = "ara" + outinfo
        elif string.find(strInfo, '''title="Bengali''') > 0:
            outinfo = "ben" + outinfo
        elif string.find(strInfo, '''title="Tamil''') > 0:
            outinfo = "tam" + outinfo
        elif string.find(strInfo, '''title="Russo''') > 0:
            outinfo = "rus" + outinfo
        elif string.find(strInfo, '''title="Turco''') > 0:
            outinfo = "tur" + outinfo
        elif string.find(strInfo, '''title="Curdo''') > 0:
            outinfo = "kur" + outinfo
        elif string.find(strInfo, '''title="Afghan''') > 0:
            outinfo = "afg" + outinfo
        elif string.find(strInfo, '''title="Ceco''') > 0:
            outinfo = "cze" + outinfo
        elif string.find(strInfo, '''title="Ungherese''') > 0:
            outinfo = "hun" + outinfo
        elif string.find(strInfo, '''title="Olandese''') > 0:
            outinfo = "ned" + outinfo
        elif string.find(strInfo, '''title="Spagnolo''') > 0:
            outinfo = "esp" + outinfo
        elif string.find(strInfo, '''title="Macedone''') > 0:
            outinfo = "mac" + outinfo
        elif string.find(strInfo, '''title="Tailandese''') > 0:
            outinfo = "tha" + outinfo
        elif string.find(strInfo, '''title="Vietnamita''') > 0:
            outinfo = "vie" + outinfo
        elif string.find(strInfo, '''title="Greco''') > 0:
            outinfo = "gre" + outinfo
        elif string.find(strInfo, '''title="Somali''') > 0:
            outinfo = "som" + outinfo
        elif string.find(strInfo, '''title="Berbere''') > 0:
            outinfo = "ber" + outinfo
        elif string.find(strInfo, '''title="Azero''') > 0:
            outinfo = "aze" + outinfo
        else:
            outinfo = "oth" + outinfo
        
        return outinfo
    







    
    
    
    
    
    
    
    
    
    # parse bouquet section
    def __parse_bouquet(self, bouquetStr):
        
        # offsets
        tra1=0
        tra2=0
        
        bqtList = list()
        
        tra1 = string.find(bouquetStr, ">")
        tra2 = string.find(bouquetStr, '''href="''', tra1+1)
        
        # check for only one bouquet
        if tra2 < 0:
            tra2 = string.find(bouquetStr, "<", tra1+1)
            bqtList.append(bouquetStr[tra1+1:tra2].replace(" ", ""))
            return bqtList
        
        tra1 = tra2
        
        # loop for each other bouquet
        while tra1 > 0:
            tra1 = string.find(bouquetStr, ">", tra1+6)
            tra2 = string.find(bouquetStr, "</a>", tra1+1)
            bqtList.append(bouquetStr[tra1+1:tra2].replace(" ", ""))
            
            tra1 = string.find(bouquetStr, '''href="''', tra2+3)
        
        return bqtList
        
        
        
        
        
        
        
        
        
        
    # write output file (channels list)
    def __write_output_file(self):
        outputStr = ""
        outputStrMissing = ""
        
        # read and parse config file if is required
        if self.__args.configfile != None:    
            # update output string using config data
            
            for item in self.__outputList:
                if string.find(item, ':') >= 0:
                    # channels informations founded on KingOfSat, so add it
                    outputStr += item + "\n"
                
                else:
                    # channels not founded, added in missing list
                    outputStrMissing += item + "\n"
                    
        
        else:
            # update output string with all data
            for item in range(0, len(self.__name_bouquets)):
                outputStr += ":[ " + self.__name_bouquets[item] + " ]\n" + self.__channels_bouquets[item]
        
        
        # write data in to output file
        file = open(self.__args.outfile, "w")
        file.write(outputStr)
        file.close()
        
        # check for missing channels
        if (len(outputStrMissing) > 0):
            # write data in missing output file
            file = open(self.__args.outfile + '.missing', "w")
            file.write(outputStrMissing)
            file.close()        
        
        
        
        
        
        



# EntryPoint
app=getchannels()





