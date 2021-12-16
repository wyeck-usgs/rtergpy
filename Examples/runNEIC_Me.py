# -*- coding: utf-8 -*-
# wyeck 

''' 
Convience code to take NEIC event ID, grab information from comcat and run rtergoy
'''

from rtergpy.run import defaults, event, etime2name, src2ergs
from obspy import UTCDateTime
import argparse
from libcomcat.search import get_event_by_id
from obspy.imaging.beachball import mt2plane, MomentTensor
from numpy import abs, sort, log10
from numpy.linalg import eig

Defaults=defaults()
Event=event()

# Takes a event ID and gets the required input for rtergpy
def grabFromComcat(evid):
    
    """ 
    Grabs the prefered origin info from COMCAT given a event ID
    Args:
    evid (str): the event ID (e.g., us6000e0k5)
    """
    
    event = get_event_by_id(evid)
    lat = event.latitude
    lon = event.longitude
    depth = event.depth
    eloc = [lat,lon,depth]
    etime = UTCDateTime(event.time)
    mts = event.getProducts("moment-tensor")[0]
    
    try:
        magtype = mts["derived-magnitude-type"]
    
    except Exception as e:
        magtype = "??"
        print("Comcat Mag Type Error (Unkown Type)")
   
    mpp = float(mts["tensor-mpp"])
    mrr = float(mts["tensor-mrr"])
    mtt = float(mts["tensor-mtt"])
    mrt = float(mts["tensor-mrt"])
    mtp = float(mts["tensor-mtp"])
    mrp = float( mts["tensor-mrp"])
    MT = MomentTensor(mrr, mpp, mtt, mrt, mrp, mtp,0)
    nodalplane = mt2plane(MT)
    emech = [nodalplane.strike,nodalplane.dip,nodalplane.rake]
    eigs = abs(sort(eig(MT.mt)[0]))
    mo = 0.5 * (abs(eigs[0]) + abs(eigs[2]))
    mw = (2.0 / 3.0) * (log10(mo) - 9.1)

    return eloc, etime, emech, mw


def main():
    parser = argparse.ArgumentParser(
        description="Convience code to Run rtergpy from a NEIC event id"
    )
    parser.add_argument(
        "-evid",
        "--Event_ID",
        type=str,
        required=True,
        help="The eventID of the event to process (e.g., us6000e0k5)",
    )
    
    parser.add_argument(
        "-nd",
        "--newData",
        type=bool,
        required=False,
        default=True,
        help="If you should grab new data or use previously downloaded data",
    )
    
    parser.add_argument(
        "-ec",
        "--eventCount",
        type=str,
        required=False,
        default="00",
        help="The event count",
    )
    
    args = parser.parse_args()

    eloc, etime, emech, mw = grabFromComcat(args.Event_ID)
    Event.ecount=args.eventCount
    Event.newData=args.newData
    Event.eventname=etime2name(etime,ecount=Event.ecount)
    Event.origin=[eloc,etime]
    Event.focmech=emech
    Event.Mw = mw
    
    print("Event ID:", args.Event_ID)
    print("rtergpy Name:", Event.eventname)
    print("Origin Time:", etime)
    print("Location:", eloc)
    print("Nodal Plane:", emech)
    print("Mw:", mw)

    src2ergs(Defaults=Defaults,Event=Event)  

if __name__ == "__main__":
    main()
