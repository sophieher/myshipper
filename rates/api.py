from requesters import RatesRequester, LabelRequester

# Does the request cycle, 
# fills the dictionary of the requester
# makes the request to USPS then builds and returns a response
def do_request(requester):
    requester.fill_dict_of_requests()# = labels
    root = requester.make_request()
    if root.tag == ('Error'): print root.find('Description').text
    return requester.create_response(root)
    
# GET helper for view for rates retrieval 
import json
import ast

def get_rates_from_usps(params):  
    #   handles get requests with json string payload/params, as well as simple dictionaries
    #   if there are multiple packages
    try:         
        for x in params:
            l=json.loads(x)
        d = {}
        for k in l:
            if k.startswith('pkg'):
                d[k]= do_request( RatesRequester(l.get(k)) )
        return {"data":d}
    except:
        d = {}        
        for k in params:
            if k.startswith('pkg'):
                value = params.get(k)
                v = ast.literal_eval(value)
                d[k]= do_request( RatesRequester(v) )
                return {"data":d}
            else:
                return {"data": do_request(RatesRequester(params))}


# GET helper for view for label retrieval    
def get_label_from_usps(params):
    return do_request(LabelRequester(params))
