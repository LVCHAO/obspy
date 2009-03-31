# -*- coding: utf-8 -*-
"""
Wrapper class for libmseed - The Mini-SEED library.

Currently only supports MiniSEED files with integer data values.

This library is free software; you can redistribute it and/or modify
it under the terms of the GNU Library General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License (GNU-LGPL) for more details.  The
GNU-LGPL and further information can be found here:
http://www.gnu.org/
"""

from obspy.mseed.headers import MSRecord, MSTraceGroup, MSTrace, HPTMODULUS
import ctypes as C
from datetime import datetime
from time import mktime, tzset
import math
import os
import sys
import platform

#Set global timezone to UTC.
os.environ['TZ'] = 'UTC'
tzset()

#Import libmseed library.
if sys.platform=='win32':
    lib_name = 'libmseed.win32.dll'
else:
    if platform.architecture()[0] == '64bit':
        lib_name = 'libmseed.lin64.so'
    else:
        lib_name = 'libmseed.so'
clibmseed = C.CDLL(os.path.join(os.path.dirname(__file__), 'libmseed', 
                                lib_name))


class libmseed(object):
    """
    Wrapper class for libmseed.
    """

    def printtracelist(self,filename,timeformat= 0,details = 0, gaps=0):
        """
        Prints information about the traces in a Mini-SEED file using the libmseed
        method printtracelist.
        
        Prints all informations to stdout.
        
        filename          - Name of file to read Mini-SEED data from
        timeformat      - Controls the format of the resulting time string, default = 0
                                    0 : SEED time format (2005,146,00:00:00.000000)
                                    1 : ISO time format (2005-05-26T00:00:00.000000)
                                    2 : Epoch time, seconds since the epoch (1117065600.00000000)
        details             - If the details flag is greater than 0 the sample rate and 
                                  sample count are printed for each trace, default = 0
        gaps                - If the gaps flag is greater than zero the time gap from the 
                                  previous MSTrace (if the source name matches) is printed, 
                                  default = 0
        """
        mstg = self.readTraces(filename, dataflag = 0,skipnotdata = 0)
        clibmseed.mst_printtracelist(mstg,timeformat,details,gaps)
    
    def printgaplist(self,filename,timeformat= 0,mingap = 0, maxgap=0):
        """
        Prints a formatted list of the gaps between MSTrace segments in the
        given MSTraceGroup to stdout. If mingap or maxgap is not NULL their 
        values will be enforced and only gaps/overlaps matching their implied
        criteria will be printed.
        
        Uses the libmseed function printgapslist.
        
        filename          - Name of file to read Mini-SEED data from
        timeformat      - Controls the format of the resulting time string, defaults to 0
                                    0 : SEED time format (2005,146,00:00:00.000000)
                                    1 : ISO time format (2005-05-26T00:00:00.000000)
                                    2 : Epoch time, seconds since the epoch (1117065600.00000000)
        mingap            - defaults to 0
        maxgap           - defaults to 0
        """
        mstg = self.readtraces(filename, dataflag = 0, skipnotdata = 0)
        clibmseed.mst_printgaplist(mstg,timeformat,mingap,maxgap)
    
    def msr2dict(self, m):
        """
        """
        h = {}
        h['reclen'] = m.contents.reclen
        h['sequence_number'] = m.contents.sequence_number
        h['network'] = m.contents.network
        h['station'] = m.contents.station
        h['location'] = m.contents.location
        h['channel'] = m.contents.channel
        h['dataquality'] = m.contents.dataquality
        h['starttime'] = m.contents.starttime
        h['samprate'] = m.contents.samprate
        h['samplecnt'] = m.contents.samplecnt
        h['encoding'] = m.contents.encoding
        h['byteorder'] = m.contents.byteorder
        h['encoding'] = m.contents.encoding
        h['sampletype'] = m.contents.sampletype
        return h

    def mst2dict(self, m):
        """
        Return dictionary from MSTrace Object m, leaving the attributes
        datasamples, ststate and next out
        """
        h = {}
        h["network"] = m.contents.network
        h["station"] = m.contents.station
        h["location"] = m.contents.location
        h["channel"] = m.contents.channel
        h["dataquality"] = m.contents.dataquality
        h["type"] = m.contents.type
        h["starttime"] = m.contents.starttime
        h["endtime"] = m.contents.endtime
        h["samprate"] = m.contents.samprate
        h["samplecnt"] = m.contents.samplecnt
        h["numsamples"] = m.contents.numsamples
        h["sampletype"] = m.contents.sampletype
        return h

    def dict2mst(self, m, h):
        """
        Takes dictionary containing MSTrace header data and writes them to the
        MSTrace Group
        """
        m.contents.network =h["network"]
        m.contents.station = h["station"] 
        m.contents.location = h["location"]
        m.contents.channel = h["channel"]
        m.contents.dataquality = h["dataquality"]
        m.contents.type = h["type"]
        m.contents.starttime = h["starttime"]
        m.contents.endtime = h["endtime"]
        m.contents.samprate = h["samprate"]
        m.contents.samplecnt = h["samplecnt"]
        m.contents.numsamples = h["numsamples"]
        m.contents.sampletype = h["sampletype"]
        
    def compareHeaders(self, header1, msrecord):
        if len(msrecord) == 0:
            return True
        #msrecord[len(msrecord)-1][0]
        else:
            return False
    
    def read_ms_using_traces(self, filename, dataflag = 1):
        """
        Read Mini-SEED file. Header, Data and numtraces are returned

        filename        - Name of file to read Mini-SEED data from
        timetol           - Time tolerance, default is 1/2 sample period (-1)
        sampratetol   - Sample rate tolerance, default is rate dependent (-1)
        verbosity       - Level of diagnostic messages, default 0
        """
        #Creates MSTraceGroup Structure
        mstg = self.readTraces(filename)
        data=[]
        header=[]
        mst = mstg.contents.traces
        numtraces = mstg.contents.numtraces
        for _i in range(numtraces):
            data.extend(mst.contents.datasamples[0:mst.contents.numsamples])
            header.append(self.mst2dict(mst))
            mst = mst.contents.next
        return header[0],data, numtraces
    
    def readMSusingRecords(self, filename):
        """
        Reads a given Mini-SEED file and parses all information.
        
        Structure of the returned list:
        [[header for trace 1, data] , [header for trace 2, data], ...]
        """
        msrecord=[]
        retcode=0
        while retcode == 0:
            msr, retcode = self.read_MSRec(filename)
            if retcode == 0:
                header=self.msr2dict(msr)
                #Sanity check
                if header['samplecnt'] != msr.contents.numsamples:
                    print "Warning: The number of samples unpacked does not"
                    print "correspond with the number of samples specified in the header."
#                if len(msrecord) == 0:
#                data=msr.contents.datasamples[0:msr.contents.numsamples]
                if self.compareHeaders(header, msrecord):
                    print "Same Trace"
                else:
                    msrecord.append([header, 0])
        return msrecord

    def read_MSRec(self, filename, reclen = -1, dataflag = 1, 
                   skipnotdata = 1, verbose = 0):
        """
        Reads Mini-SEED file and populates MS Record data structure with subsequent
        calls.
        
        filename        - Mini-SEED file to be read
        reclen            - If reclen is 0 the length of the first record is auto-
                                detected. All subsequent records are then expected to
                                have the same record length.
                                If reclen is negative the length of every record is
                                automatically detected.
                                Defaults to -1.
        dataflag        - Controls whether data samples are unpacked, defaults to 1
        skipnotdata   - If true (not zero) any data chunks read that to do not
                                have valid data record indicators will be skipped.
                                Defaults to true (1).
        verbose         - Controls verbosity from 0 to 2. Defaults to None (0).
        """
        #Init MSRecord structure
        clibmseed.msr_init.restype = C.POINTER(MSRecord)
        msr=clibmseed.msr_init(None)
        #Defines return type
        clibmseed.ms_readmsr.restype = C.c_int
        #Read the file and write the relevant information to msr
        retcode=clibmseed.ms_readmsr(C.pointer(msr), filename, C.c_int(reclen),
                             None, None,
                             C.c_short(skipnotdata), C.c_short(dataflag),
                             C.c_short(verbose))
        return msr,retcode

    def populate_MSTG(self, header, data, numtraces=1):
        """
        Populates MSTrace_Group structure from given header, data and
        numtraces and returns the MSTrace_Group
        """
        #Init MSTraceGroupint
        clibmseed.mst_initgroup.restype = C.POINTER(MSTraceGroup)
        mstg = clibmseed.mst_initgroup(None)
        #Init MSTrace object
        clibmseed.mst_init.restype = C.POINTER(MSTrace)
        #Connect Group with Traces
        mstg.contents.traces=clibmseed.mst_init(None)
        #Write header in MSTrace structure
        self.dict2mst(mstg.contents.traces, header)
        #Needs to be redone, dynamic??
        mstg.contents.numtraces=numtraces
        #Create void pointer and allocates more memory to it
        tempdatpoint=C.c_void_p()
        C.resize(tempdatpoint,
                 clibmseed.ms_samplesize(C.c_char(header['sampletype']))*
                 header['numsamples'])
        #Set pointer to tempdatpoint
        mstg.contents.traces.contents.datasamples=C.pointer(tempdatpoint)
        #Write data in MSTrace structure
        for i in range(header['numsamples']):
            mstg.contents.traces.contents.datasamples[i]=C.c_void_p(data[i])
        return mstg

    def mst2file(self, mst, outfile, reclen, encoding, byteorder, flush, verbose):
        """
        Takes MS Trace object and writes it to a file
        """
        mseedfile=open(outfile, 'wb')
        #Initialize packedsamples pointer for the mst_pack function
        self.packedsamples = C.pointer(C.c_int(0))
        #Callback function for mst_pack to actually write the file
        def record_handler(record, reclen, _stream):
            mseedfile.write(record[0:reclen])
        #Define Python callback function for use in C function
        RECHANDLER = C.CFUNCTYPE(None, C.POINTER(C.c_char), C.c_int, C.c_void_p)
        rec_handler = RECHANDLER(record_handler)
        #Pack the file into a MiniSEED file
        clibmseed.mst_pack(mst, rec_handler, None, reclen, encoding, byteorder,
                           self.packedsamples, flush, verbose, None)
        mseedfile.close()
    
    def write_ms(self,header,data, outfile, numtraces=1, reclen= -1,
                 encoding=-1, byteorder=-1, flush=-1, verbose=0):
        """
        Write Miniseed file from header, data and numtraces
        
        header    - Dictionary containing the header files
        data      - List of the datasamples
        outfile   - Name of the output file
        numtraces - Number of traces in trace chain (Use??)
        reclen    - should be set to the desired data record length in bytes
                    which must be expressible as 2 raised to the power of X 
                    where X is between (and including) 8 to 20. -1 defaults to
                    4096
        encoding  - should be set to one of the following supported Mini-SEED
                    data encoding formats: DE_ASCII (0), DE_INT16 (1), 
                    DE_INT32 (3), DE_FLOAT32 (4), DE_FLOAT64 (5), DE_STEIM1 (10)
                    and DE_STEIM2 (11). -1 defaults to STEIM-2 (11)
        byteorder - must be either 0 (LSBF or little-endian) or 1 (MBF or 
                    big-endian). -1 defaults to big-endian (1)
        flush     - if it is not zero all of the data will be packed into 
                    records, otherwise records will only be packed while there
                    are enough data samples to completely fill a record.
        verbose   - controls verbosity, a value of zero will result in no 
                    diagnostic output.
        """
        #Populate MSTG Structure
        mstg=self.populate_MSTG(header, data, numtraces)
        #Write File from MS-Trace structure
        self.mst2file(mstg.contents.traces, outfile, reclen, encoding, byteorder,
                      flush, verbose)
    
    def cut_ms(self, data, header, stime, cutsamplecount, outfile='cut.mseed'):
        """
        Takes a data file list, a header dictionary, a starttime, the number of 
        samples to cut and writes it in outfile.
        stime             - The time in microseconds with the origin set to the
                                      beginning of the file
        cutsamplecount  - The number of samples to cut
        outfile                  - filename of the Record to write
        """
        samprate_in_microsecs = header['samprate']/1e6
        #Modifiy the header
        header['starttime'] = header['starttime'] + stime
        header['endtime'] = int(header['starttime'] + cutsamplecount/\
                                samprate_in_microsecs)
        header['numsamples'] = cutsamplecount
        header['samplecnt'] = cutsamplecount
        #Make new data list, some rounding issues need to be solved
        cutdata=data[int(stime/samprate_in_microsecs):cutsamplecount+1]
        #Write cutted file
        self.write_ms(header, cutdata, outfile)
    
    def printrecordinfo(self, file):
        """
        Reads Mini-SEED file using subsequent calls to read_MSRec and prints
        general information about all records in the file and any gaps/overlaps
        present in the file
        """
        print "Records in",file,":"
        print "---------------------------------------------------"
        retcode=0
        oldstarttime=0
        while retcode == 0:
            msr, retcode=self.read_MSRec(file, dataflag=0, skipnotdata=0)
            if retcode == 0:
                    if oldstarttime!=0:
                        if msr.contents.starttime-oldstarttime==0:
                            print "NO GAPS/OVERLAPS"
                        elif msr.contents.starttime-oldstarttime<0:
                            print "OVERLAP"
                        else:
                            print "GAP"
                    oldstarttime=long(msr.contents.starttime+\
                                      msr.contents.samplecnt*\
                                      (1/msr.contents.samprate)*1e6)
                    print "Sequence number:",msr.contents.sequence_number,"--",
                    print "starttime:",msr.contents.starttime,", # of samples:",
                    print msr.contents.samplecnt,"=> endtime :",
                    print oldstarttime
    
    def readTraces(self, filename, reclen = -1, timetol = -1, sampratetol = -1,
                   dataflag = 1, skipnotdata = 1, verbose = 0):
        """
        Reads MiniSEED data from file. Returns MSTraceGroup structure.
        
        @param filename: Mini-SEED file to be read.
        @param reclen: If reclen is 0 the length of the first record is auto- 
            detected. All subsequent records are then expected to have the 
            same record length. If reclen is negative the length of every 
            record is automatically detected. Defaults to -1.
        @param timetol: Time tolerance, default to -1 (1/2 sample period).
        @param sampratetol: Sample rate tolerance, defaults to -1 (rate 
            dependent)
        @param dataflag: Controls whether data samples are unpacked, defaults 
            to 1
        @param skipnotdata: If true (not zero) any data chunks read that to do 
            not have valid data record indicators will be skipped. Defaults to 
            true (1).
        @param verbose: Controls verbosity from 0 to 2. Defaults to None (0).
        """
        # Creates MSTraceGroup Structure
        mstg = C.pointer(MSTraceGroup())
        # Uses libmseed to read the file and populate the MSTraceGroup structure
        errcode = clibmseed.ms_readtraces(
            C.pointer(mstg), filename, C.c_int(reclen), 
            C.c_double(timetol), C.c_double(sampratetol),
            C.c_short(dataflag), C.c_short(skipnotdata), 
            C.c_short(dataflag), C.c_short(verbose))
        if errcode != 0:
            assert 0, "\n\nError while reading Mini-SEED file: "+filename
        #Reset memory
        self.resetMs_readmsr()
        return mstg
    
    def resetMs_readmsr(self):
        """
        Cleans memory and resets the clibmseed.ms_readmsr() function.
        
        This function needs to be called after reading a Mini-SEED file with
        any of the provided methods if you want to read another Mini-SEED file
        without restarting Python. If this is not done it will probably still
        work but raise a warning.
        """
        clibmseed.msr_init.restype = C.POINTER(MSRecord)
        msr=clibmseed.msr_init(None)
        clibmseed.ms_readmsr(msr, None, 0, None, None, 0, 0, 0)
        
    def getFirstRecordHeaderInfo(self, file):
        """
        Takes Mini-SEED file string and returns some information from the
        header of the first record.
        
        Returns a dictionary containing some header information from the first
        record of the Mini-SEED file only. It returns the location, network,
        station and channel information.
        
        @param file: Mini-SEED file string.
        
        """
        #Read first header only.
        msr = self.read_MSRec(file, dataflag = 0)
        header = {}
        chain = msr[0].contents
        #Header attributes to be read.
        attributes = ('location', 'network', 'station', 'channel')
        #Loop over attributes.
        for _i in attributes:
            header[_i] = getattr(chain, _i)
        return header
    
    def getStartAndEndTime(self, file):
        """
        Returns the start- and endtime of a Mini-SEED file as a tuple of two
        Python datetime objects.
        
        This method only reads the first and the last record. Thus it will work
        only work correctly for files containing only one trace.
        
        @param file: Mini-SEED file string.
        """
        #Read starttime and record length from first header.
        msr = self.read_MSRec(file, dataflag = 0)
        chain = msr[0].contents
        starttime = chain.starttime
        record_length = chain.reclen
        #Cleanup memory and close old msr file.
        self.resetMs_readmsr()
        #Open Mini-SEED file and write last record into temporary file.
        mseed_file = open(file, 'rb')
        mseed_file.seek(-record_length, 2)
        temp_record = open('temp', 'wb')
        temp_record.write(mseed_file.read(record_length))
        mseed_file.close()
        temp_record.close()
        #Read last record.
        msr = self.read_MSRec('temp', dataflag = 0)
        chain = msr[0].contents
        #Calculate endtime.
        endtime = chain.starttime + (chain.samplecnt -1) / chain.samprate *\
                                                                    HPTMODULUS
        #Remove temporary file
        os.remove('temp')
        return (self.mseedtimestringToDatetime(starttime),
                self.mseedtimestringToDatetime(endtime))
        
    def datetimeToMseedtimestring(self, dtobj):
        """
        Takes datetime object and returns an epoch time in ms.
        
        @param dtobj: Datetime object.
        """
        return long((mktime(dtobj.timetuple()) * HPTMODULUS)+dtobj.microsecond)
    
    def mseedtimestringToDatetime(self, timestring):
        """
        Takes Mini-SEED timestring and returns a Python datetime object.
        
        @param timestring: Mini-SEED timestring (Epoch time string in ms).
        """
        return datetime.utcfromtimestamp(timestring / HPTMODULUS)
    
    def isRateTolerable(self, sr1, sr2):
        """
        Tests default sample rate tolerance: abs(1-sr1/sr2) < 0.0001
        """
        return math.fabs(1.0 - (sr1 / float(sr2))) < 0.0001
    
    def printGapList(self, filename, time_tolerance = -1, 
                     samprate_tolerance = -1, min_gap = None, max_gap = None):
        """
        Print gap/overlap list summary information for the given filename.
        """
        result = self.getGapList(filename, time_tolerance, samprate_tolerance, 
                                 min_gap, max_gap)
        print "%-17s %-26s %-26s %-5s %-8s" % ('Source', 'Last Sample', 
                                               'Next Sample', 'Gap', 'Samples')
        for r in result:
            print "%-17s %-26s %-26s %-5s %-.8g" % ('_'.join(r[0:4]), 
                                                    r[4].isoformat(), 
                                                    r[5].isoformat(), 
                                                    r[6], r[7])
        print "Total: %d gap(s)" % len(result)
    
    def getGapList(self, filename, time_tolerance = -1, 
                   samprate_tolerance = -1, min_gap = None, max_gap = None):
        """
        Returns gaps, overlaps and trace header information of a given file.
        
        Each item has a starttime and a duration value to characterize the gap.
        The starttime is the last correct data sample. If no gaps are found it
        will return an empty list.
        
        @param time_tolerance: Time tolerance while reading the traces, default 
            to -1 (1/2 sample period).
        @param samprate_tolerance: Sample rate tolerance while reading the 
            traces, defaults to -1 (rate dependent).
        @param min_gap: Omit gaps with less than this value if not None. 
        @param max_gap: Omit gaps with greater than this value if not None.
        @return: List of tuples in form of (network, station, location, 
            channel, starttime, endtime, gap, samples) 
        """
        # read file
        mstg = self.readTraces(str(filename), dataflag = 0, skipnotdata = 0,
                               timetol = time_tolerance,
                               sampratetol = samprate_tolerance)
        gap_list = []
        # iterate through traces
        cur = mstg.contents.traces.contents
        for _ in xrange(mstg.contents.numtraces-1):
            next = cur.next.contents
            # Skip MSTraces with 0 sample rate, usually from SOH records
            if cur.samprate == 0:
                cur = next
                continue
            # Check that sample rates match using default tolerance
            if not self.isRateTolerable(cur.samprate, next.samprate):
                msg = "%s Sample rate changed! %.10g -> %.10g\n"
                print msg % (cur.samprate, next.samprate)
            gap = (next.starttime - cur.endtime) / HPTMODULUS
            # Check that any overlap is not larger than the trace coverage
            if gap < 0:
                if next.samprate:
                    delta =  1 / float(next.samprate)
                else:
                    delta = 0
                temp = (next.endtime - next.starttime) / HPTMODULUS + delta
                if (gap * -1) > temp:
                    gap = -1 * temp
            # Check gap/overlap criteria
            if min_gap and gap < min_gap:
                cur = next
                continue
            if max_gap and gap > max_gap:
                cur = next
                continue
            # Number of missing samples
            nsamples = math.fabs(gap) * cur.samprate
            if gap > 0:
                nsamples-=1
            else:
                nsamples+=1
            # Convert to python datetime objects
            time1 = datetime.utcfromtimestamp(cur.endtime / HPTMODULUS)
            time2 = datetime.utcfromtimestamp(next.starttime / HPTMODULUS)
            gap_list.append((cur.network, cur.station, cur.location, 
                             cur.channel, time1, time2, gap, nsamples))
            cur = next
        return gap_list
    
    def graph_create_min_max_list(self, file, width, timespan = ()):
        """
        Returns a list that consists of pairs of minimum and maxiumum data
        values.
        
        Currently only supports files with one continuous trace.
        
        @param file: Mini-SEED file string
        @param width: desired width in pixel of the data graph/Number of pairs
            of mimima and maxima.
        @param timespan: Tuple of two datetime objects. The first is the
            starttime and the second the endtime. Use 0 for either of the two
            times and the start- or endtime will be set to the correponding
            time in the file.
        """
        minmaxlist=[]
        #Read traces using readTraces.
        mstg = self.readTraces(file, skipnotdata = 0)
        if mstg.contents.numtraces == 1:
            chain = mstg.contents.traces.contents
            #Check whether the whole graph should be processed.
            if timespan == () or timespan == (0,0):
                #Number of datasamples in one pixel.
                stepsize = chain.numsamples/width
                #Loop over datasamples and append to minmaxlist.
                for _i in range(width):
                    tempdatlist = chain.datasamples[_i*stepsize:
                                                    (_i+1)*stepsize]
                    minmaxlist.append([min(tempdatlist),max(tempdatlist)])
                return minmaxlist
            else:
                #Catch currently not supported times.
                if timespan[0] == 0 or timespan[1] == 0 or \
                self.datetimeToMseedtimestring(timespan[0]) >= chain.starttime\
                or self.datetimeToMseedtimestring(timespan[1]) <= \
                chain.endtime:
                    raise ValueError('Sorry. Times currently not supported')
                #Convert start and endtime.
                starttime = self.datetimeToMseedtimestring(timespan[0])
                endtime = self.datetimeToMseedtimestring(timespan[1])
                file_starttime = chain.starttime
                file_endtime = chain.endtime
                #Number of datasamples in one pixel.
                stepsize = (chain.numsamples / width) * (endtime - starttime)/\
                                                (file_endtime - file_starttime)
                #Number of empty pixels at the beginning.
                if starttime < file_starttime:
                    empty_pixels_at_start = int(((file_starttime - starttime)/\
                        1e6 * chain.samprate) / stepsize)
                else:
                    empty_pixels_at_start = 0
                #Number of empty pixels at the end.
                if endtime > file_endtime:
                    empty_pixels_at_end = int(((endtime - file_endtime)/\
                        1e6 * chain.samprate) / stepsize)
                else:
                    empty_pixels_at_end = 0
                #Loop over pixels.
                for _i in range(empty_pixels_at_start):
                    minmaxlist.append([])
                #Offset for list indices.
                offset = (file_starttime - starttime) % stepsize
                #First drawn pixel
                tempdatlist = chain.datasamples[0 : stepsize - offset]
                minmaxlist.append([min(tempdatlist),max(tempdatlist)])
                #Loop over middle pixels.
                for _i in range(width - empty_pixels_at_end - 
                                empty_pixels_at_start - 2):
                    tempdatlist = chain.datasamples[(_i+1)*stepsize - offset:
                                                    (_i+2)*stepsize - offset]
                    minmaxlist.append([min(tempdatlist),max(tempdatlist)])
                #Last drawn pixel
                tempdatlist = chain.datasamples[chain.samplecnt - offset : \
                                                chain.samplecnt]
                minmaxlist.append([min(tempdatlist),max(tempdatlist)])
                for _i in range(empty_pixels_at_end):
                    minmaxlist.append([])
                    #Reset memory
                    self.resetMs_readmsr()
                return minmaxlist
        else:
            raise ValueError('Currently plotting is only supported for files '+
                             'containing one continuous trace.')
        #Reset memory
        self.resetMs_readmsr()
    
    def graph_create_graph(self, file, outfile = None, format = None,
                           size = (1024, 768), timespan = (), dpi = 100,
                           color = 'red', bgcolor = 'white',
                           transparent = False, minmaxlist = False):
        """
        Creates a graph of any given Mini-SEED file. It either saves the image
        directly to the file system or returns an binary image string.
        
        Currently only supports files with one continuous trace. I still have
        to figure out how to remove the frame around the graph and create the
        option to set a start and end time of the graph.
        
        The option to set a start- and endtime to plot currently only works
        for starttime smaller and endtime greater than the file's times.
        
        For all color values you can use legit html names, html hex strings
        (e.g. '#eeefff') or you can pass an R , G , B tuple, where each of
        R , G , B are in the range [0,1]. You can also use single letters for
        basic builtin colors ('b' = blue, 'g' = green, 'r' = red, 'c' = cyan,
        'm' = magenta, 'y' = yellow, 'k' = black, 'w' = white) and gray shades
        can be given as a string encoding a float in the 0-1 range.
        
        @param file: Mini-SEED file string
        @param outfile: Output file string. Also used to automatically
            determine the output format. Currently supported is emf, eps, pdf,
            png, ps, raw, rgba, svg and svgz output.
            Defaults to None.
        @param format: Format of the graph picture. If no format is given the
            outfile parameter will be used to try to automatically determine
            the output format. If no format is found it defaults to png output.
            If no outfile is specified but a format is than a binary
            imagestring will be returned.
            Defaults to None.
        @param size: Size tupel in pixel for the output file. This corresponds
            to the resolution of the graph for vector formats.
            Defaults to 1024x768 px.
        @param timespan: Tuple of two datetime objects. The graph will be
            plotted between the two times. Use 0 for either of the two times
            and it will be set to start- or endtime of the file.
            Defaults to () (All datasamples will be plotted).
        @param dpi: Dots per inch of the output file. This also affects the
            size of most elements in the graph (text, linewidth, ...).
            Defaults to 100.
        @param color: Color of the graph. Defaults to 'red'.
        @param bgcolor: Background color of the graph. Defaults to 'white'.
        @param transparent: Make all backgrounds transparent (True/False). This
            will overwrite the bgcolor param.
            Defaults to False.
        @param minmaxlist: A list containing minimum and maximum values. If
            none is supplied it will be created automatically. Useful for
            caching.
            Defaults to False.
        """
        #Either outfile or format needs to be set.
        if not outfile and not format:
            raise ValueError('Either outfile or format needs to be set.')
        #Get a list with minimum and maximum values.
        if not minmaxlist:
            minmaxlist = self.graph_create_min_max_list(file = file,
                                                    width = size[0],
                                                    timespan = timespan)
        length = len(minmaxlist)
        #Needs to be done before importing pylab or pyplot.
        import matplotlib
        #Use AGG backend.
        matplotlib.use('AGG')
        #Importing pyplot and numpy.
        import matplotlib.pyplot as plt
        #Setup figure and axes
        fig = plt.figure(num = None, figsize = (float(size[0])/dpi,
                         float(size[1])/dpi))
        ax = fig.add_subplot(111)
        # hide axes + ticks
        ax.axison = False
        #Make the graph fill the whole image.
        fig.subplots_adjust(left=0, bottom=0, right=1, top=1)
        #Determine range for the y axis. This may not be the smartest way to
        #do it.
        miny = 99999999999999999
        maxy = -9999999999999999
        for _i in range(length):
            try:
                if minmaxlist[_i][0] < miny:
                    miny = minmaxlist[_i][0]
            except:
                pass
            try:
                if minmaxlist[_i][1] > maxy:
                    maxy = minmaxlist[_i][1]
            except:
                pass
        #Set axes and disable ticks
        plt.ylim(miny, maxy)
        plt.xlim(0,length)
        plt.yticks([])
        plt.xticks([])
        #Draw horizontal lines.
        for _i in range(length):
            if minmaxlist[_i] == []:
                pass
            else:
                #Calculate relative values needed for drawing the lines.
                yy = (float(minmaxlist[_i][0])-miny)/(maxy-miny)
                xx = (float(minmaxlist[_i][1])-miny)/(maxy-miny)
                plt.axvline(x = _i, ymin = yy, ymax = xx, color = color)
        #Save file.
        if outfile:
            #If format is set use it.
            if format:
                plt.savefig(outfile, dpi = dpi, transparent = transparent,
                    facecolor = bgcolor, edgecolor = bgcolor, format = format)
            #Otherwise try to get the format from outfile or default to png.
            else:
                plt.savefig(outfile, dpi = dpi, transparent = transparent,
                    facecolor = bgcolor, edgecolor = bgcolor)
        #Return an binary imagestring if outfile is not set but format is.
        if not outfile:
            import StringIO
            imgdata = StringIO.StringIO()
            plt.savefig(imgdata, dpi = dpi, transparent = transparent,
                    facecolor = bgcolor, edgecolor = bgcolor, format = format)
            imgdata.seek(0)
            return imgdata.read()
    
    def getMinMaxList(self, file, width):
        """
        Returns a list that consists of minimum and maximum data values.
        
        @param file: Mini-SEED file string.
        @param width: Desired width in pixel of the data graph/number of 
            values of returned data list.
        """
        # Read traces
        mstg = self.readTraces(file, skipnotdata = 0)
        chain = mstg.contents.traces.contents
        # Number of datasamples in one pixel
        if width >= chain.numsamples:
            width = chain.numsamples
        stepsize = int(chain.numsamples/width)
        # Loop over datasamples and append to minmaxlist
        data=[]
        for x in xrange(0, width):
            temp = chain.datasamples[x*stepsize:(x+1)*stepsize]
            if x%2:
                data.append(min(temp))
            else:
                data.append(max(temp))
        return data
