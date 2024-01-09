from math      import sqrt, floor
from typing    import List, Tuple, Callable
from itertools import product

import os
import json

INF_RETURN = 'inf'    # value to indicate infeasible solutions
EPS_VALUE  = 0.000001 # tolerance

INSTANCE_DIRECTORY = os.path.join( '.', 'instances' )
SOLUTION_DIRECTORY = os.path.join( '.', 'solutions' )
OUTPUT_DIRECTORY   = os.path.join( '.' )
__tempfile = 'temp.csv'

# instance : list of locations (location: dictionary of demands (demand) and coordinates (x and y), where the first locations refer to plants)
# solution : list of routes (route: list of batches (batch: list of customer indices))

def get_travel_time( locations:List[dict], loc_a:int, loc_b:int, rounding_func:Callable[[float],float]= None ) -> float:
    """
    Returns the travel time (actually, the Euclidean distance) between the given locations.

    Parameters:
        - locations:     list of location dictionaries, where first elements represent the plants
        - loc_a:         index of the 'from' location
        - loc_b:         index of the 'to' location
        - rounding_func: function to be invoked on the value to return (may be None)
            - examples: 'floor', 'lambda x: round(x,2)', etc.

    Returns: travel time from location 'loc_a' to location 'loc_b'
    """
    assert 0 <= loc_a and loc_a < len(locations), f'invalid location index ({loc_a})!'
    assert 0 <= loc_b and loc_b < len(locations), f'invalid location index ({loc_b})!'
    assert all( key in locations[loc_a].keys() for key in ['x','y'] ), f'invalid location dictionary ({locations[loc_a]})!'
    assert all( key in locations[loc_b].keys() for key in ['x','y'] ), f'invalid location dictionary ({locations[loc_b]})!'

    dist = sqrt( float((locations[loc_a]['x'] - locations[loc_b]['x'])**2 + (locations[loc_a]['y'] - locations[loc_b]['y'])**2) )

    if rounding_func is None:
        return dist
    
    return rounding_func( dist )

def evaluate( locations:List[dict], capacity:int, lifespan:int, rate:int, solution:List[List[List[int]]], rounding_func:Callable[[float],float]= None, check_feasibility:bool= True, print_reason:bool= False, print_solution:bool= False ) -> float:
    """
    Evaluates the given solution.

    Parameters:
        - locations:         instance dictionary
        - capacity:          capacity of the vehicle
        - lifespan:          lifespan of the batches
        - rate:              production rate
        - solution:          list of routes (route = list of batches (batch = list of customers))
        - rounding_func:     function to be invoked on travel times (may be None)
                               - examples: 'floor', 'lambda x: round(x,2)', etc.
        - check_feasibility: should we check solution feasibility?
        - print_reason:      should we print reason of infeasibility, if any?
        - print_solution:    should we print evaluated solution?

    Returns: makespan of the given solution
    """

    nplants = len(solution)

    # check customers, if needed
    if check_feasibility:
        visited_customers = []
        for batch in solution:
            for batch in batch:
                visited_customers.extend( batch )
        visited_customers.sort()

        if len(visited_customers) != len(locations) - nplants:
            if print_reason:
                print( f'invalid number of visited customers! Visited: {visited_customers}' )
            return INF_RETURN

        for i in range(0,len(visited_customers)):
            if visited_customers[i] != i+nplants:
                if print_reason:
                    print( f'missing customer! Visited: {visited_customers}' )
                return INF_RETURN

    makespan = 0

    # evaluate routes
    for plant in range(len(solution)):
        if print_solution:
            print( '-'*60 )

        curr_p_finish = 0
        curr_t_finish = 0

        for batch in solution[plant]:
            p_time = sum( locations[location]['demand'] for location in batch )

            if check_feasibility and capacity + EPS_VALUE <= p_time:
                if print_reason:
                    print( f'demand of batch {batch} exceeds the capacity limit ({capacity} < {p_time})!' )
                return INF_RETURN
            
            p_time /= float(rate)

            t_time = get_travel_time( locations, plant, batch[0], rounding_func )
            t_time += sum( get_travel_time( locations, batch[cust-1], batch[cust], rounding_func ) for cust in range(1,len(batch)) )

            if check_feasibility and lifespan + EPS_VALUE <= t_time:
                if print_reason:
                    print( f'batch {batch} violates lifespan constraint (last delivery= {t_time} > {lifespan})!' )
                return INF_RETURN

            max_delay = max( 0, lifespan - t_time ) # negative delay (infeasible solution!) could cause inconsistency between production finish and transportation start
            t_time += get_travel_time( locations, batch[-1], plant, rounding_func )

            earliest_p_finish = curr_p_finish + p_time

            next_p_finish = 0
            next_t_finish = 0
            if curr_t_finish <= earliest_p_finish:
                next_p_finish = curr_p_finish + p_time
                next_t_finish = next_p_finish + t_time
            else:
                next_t_finish = curr_t_finish + t_time
                next_p_finish = max( earliest_p_finish, curr_t_finish - max_delay )

            if print_solution:
                demand = sum( locations[location]['demand'] for location in batch )
                loc_str = ' -> '.join( f'{location:2d}' for location in batch )
                print( f'{demand} {p_time:6.2f} {t_time:6.2f} [{next_p_finish-p_time:8.2f} {next_p_finish:8.2f}] [{next_t_finish-t_time:8.2f} {next_t_finish:8.2f}] {loc_str}' )

            curr_p_finish = next_p_finish
            curr_t_finish = next_t_finish

        makespan = max( makespan, curr_t_finish )

    if print_solution:
        print( '-'*60 )

    return makespan
    
def read_geismar_instance( i:int ) -> List[dict]:
    """
    Reads and returns the corresponding instance of Geismar et al.
    
    Parameters:
        - i: index of the desired instance (1,2,3,4,5,6)

    Returns: instance
    """

    with open( os.path.join( INSTANCE_DIRECTORY, 'geismar', f'instance_i{i}.json' ) ) as ifile:
        return json.load( ifile )
    
def read_canatasagun_instance( dem:int, loc:int, n:int, p:int, i:int ) -> List[dict]:
    """
    Reads and returns the corresponding instance of Can Atasagun & Karaoglan.
    
    Parameters:
        - dem:   demand distribution (1: [100,200]; 2: [100,300])
        - loc:   space distribution (1: [-100,100]; 2: [-150,150]; 3: [-200,200])
        - (n,p): number of customers and plants ((10,2),(20,2),(20,3),(30,2),(30,3),(40,2),(40,3),(50,2),(50,3),(100,3),(100,4),(100,5))
        - i:     index of the desired instance (1,2,3)

    Returns: instance
    """

    with open( os.path.join( INSTANCE_DIRECTORY, 'canatasagun', f'instance_dem{dem}_loc{loc}_n{n}_p{p}_i{i}.json' ) ) as ifile:
        return json.load( ifile )
    
def read_solution_for_geismar_instance( directory:str, i:int, Q:int, B:int, r:int ) -> List[List[List[int]]]:
    """
    Reads solution for the corresponding instance of Geismar et al.

    Parameters:
        - directory: solution directory
        - i:         instance
        - Q:         capacity
        - B:         lifespan
        - r:         production rate

    Returns: solution
    """

    filename = os.path.join( directory, f'sol_i{i}_Q{Q}_B{B}_r{r}.json' )

    with open( filename, 'r' ) as f:
       return [ json.load( f ) ]

def read_solution_for_canatasagun_instance( directory:str, dem:int, loc:int, n:int, p:int, i:int, Q:int, B:int, r:int ) -> List[List[List[int]]]:
    """
    Reads solution for the corresponding instance of Can Atasagun & Karaoglan.

    Parameters:
        - directory: solution directory
        - dem:       demand distribution type
        - loc:       space distribution type
        - n:         number of customers
        - p:         number of plants
        - i:         instance
        - Q:         capacity
        - B:         lifespan
        - r:         production rate

    Returns: solution
    """

    filename = os.path.join( directory, f'sol_dem{dem}_loc{loc}_n{n}_p{p}_i{i}_Q{Q}_B{B}_r{r}.json' )
    
    with open( filename, 'r' ) as f:
        return json.load( f )
   
def evaluate_vns_solutions_for_geismar_instances( instances:List[int], capacities:List[int], lifespans:List[int], rates:List[int], rounding_func:Callable[[float],float]= None ) -> None:
    """
    Evaluates the solutions for Geismer et al. instances of the variable neighborhood search of Horvath.

    Parameters:
        - instances:     instances to evaluate
        - capacities:    capacity values to evaluate with
        - lifespans:     lifespan values to evaluate with
        - rates:         production rates to evaluate with
        - rounding_func: rounding function
    """

    directory  = os.path.join( SOLUTION_DIRECTORY, 'geismar', 'horvath_vns' )
    outputfile = os.path.join( OUTPUT_DIRECTORY, __tempfile )

    with open( outputfile, 'w' ) as f:
        for i in instances:
            instance = read_geismar_instance( i )

            for (Q,B,r) in product(capacities,lifespans,rates):
                solution = read_solution_for_geismar_instance( directory, i, Q, B, r )
                round_makespan = evaluate( instance, Q, B, r, solution, check_feasibility= True, rounding_func= rounding_func )

                f.write( f'{i};{Q};{B};{r};{round_makespan}\n' )

        print( f'values are written into "{outputfile}"' )
 
def evaluate_vns_solutions_for_canatasagun_instances( dems:List[int], locs:List[int], nps:Tuple[List[int],List[int]], instances:List[int], capacities:List[int], lifespans:List[int], rates:List[int], rounding_func:Callable[[float],float]= None  ):
    """
    Evaluates the solutions for Can Atasagun & Karaoglan instances of the variable neighborhood search of Horvath.

    Parameters:
        - ...
    """

    directory  = os.path.join( SOLUTION_DIRECTORY, 'canatasagun', 'horvath_vns' )
    outputfile = os.path.join( OUTPUT_DIRECTORY, __tempfile )

    with open( outputfile, 'w' ) as f:    
        for (dem,loc,(n,p),i) in product( dems, locs, nps, instances ):
            instance = read_canatasagun_instance( dem, loc, n, p, i )

            for (Q,B,r) in product( capacities, lifespans, rates ):
                try:
                    solution = read_solution_for_canatasagun_instance( directory, dem, loc, n, p, i, Q, B, r )
                    makespan = evaluate( instance, Q, B, r, solution, rounding_func= rounding_func, check_feasibility= True, print_reason= False, print_solution= False )
                    
                    f.write( f'{i};{Q};{B};{r};{makespan}\n' )
                except:
                    f.write( f'{i};{Q};{B};{r};-\n' )

    print( f'values are written into "{outputfile}"' )

def evaluate_lacomme_et_al_solutions_for_geismar_instances( instances:List[int], capacities:List[int], lifespans:List[int], rates:List[int], check_feasibility:bool = True ) -> None:
    """
    Evaluates the solutions for Geismar et al. instances of Lacomme et al. using several rounding functions.

    Parameters:
        - instances:         instances to evaluate
        - capacities:        capacity values to evaluate with
        - lifespans:         lifespan values to evaluate with
        - rates:             production rates to evaluate with
        - check_feasibility: should we check the feasibility of the solutions?
    """

    floor_infeasible_cases = []
    round_infeasible_cases = []

    outputfile = os.path.join( OUTPUT_DIRECTORY, __tempfile )

    with open( outputfile, 'w' ) as f:
        for i in instances:
            instance = read_geismar_instance( i )

            for (Q,B,r) in product(capacities,lifespans,rates):
                values = []
                for rep in [1,2,3,4,5]:
                    solution = read_solution_for_geismar_instance( os.path.join( SOLUTION_DIRECTORY, 'geismar', 'lacomme_et_al', f'rep{rep}' ), i, Q, B, r )

                    origi_value = evaluate( instance, Q, B, r, solution, check_feasibility= check_feasibility, rounding_func= None )
                    round_value = evaluate( instance, Q, B, r, solution, check_feasibility= check_feasibility, rounding_func= lambda x: round(x,2) )
                    floor_value = evaluate( instance, Q, B, r, solution, check_feasibility= check_feasibility, rounding_func= floor )

                    values.append( origi_value )
                    values.append( round_value )
                    values.append( floor_value )

                    if floor_value == INF_RETURN:
                        floor_infeasible_cases.append( (i,Q,B,r,rep) )
                    elif round_value == INF_RETURN:
                        round_infeasible_cases.append( (i,Q,B,r,rep) )

                f.write( f'{i};{Q};{B};{r};' + ';'.join( map(str,values) ) + '\n' )
        
        if check_feasibility:
            print( f'FLOOR infeasible cases: {len(floor_infeasible_cases):3d}' )
            print( f'ROUND infeasible cases: {len(round_infeasible_cases):3d}' )

        print( f'values are written into "{outputfile}"' )

    if check_feasibility != None:
        # collect results
        floor_dict:dict[tuple,list] = {}

        for (i,Q,B,r,rep) in floor_infeasible_cases:
            if (i,Q,B,r) not in floor_dict.keys():
                floor_dict[(i,Q,B,r)] = []
            floor_dict[(i,Q,B,r)].append( rep )

        round_dict:dict[tuple,list] = {}

        for (i,Q,B,r,rep) in round_infeasible_cases:
            if (i,Q,B,r) not in round_dict.keys():
                round_dict[(i,Q,B,r)] = []
            round_dict[(i,Q,B,r)].append( rep )

        # write results
        inffile = os.path.join( OUTPUT_DIRECTORY, __tempfile )

        with open( inffile, 'a' ) as f:
            f.write( 'floor infeasible cases (i | Q | B | r | reps):\n' )
            for ((i,Q,B,r),reps) in floor_dict.items():
                f.write( f'{i} & {Q} & {B} & {r} & {",".join(map(str,reps))}\\\\\n' )

            f.write( 'round infeasible cases (i | Q | B | r | reps):\n' )
            for ((i,Q,B,r),reps) in round_dict.items():
                f.write( f'{i} & {Q} & {B} & {r} & {",".join(map(str,reps))}\\\\\n' )

            print( f'infeasible cases, if any, are written into "{inffile}"' )

def evaluate_bestknown_solutions_for_geismar_instances( instances:List[int], capacities:List[int], lifespans:List[int], rates:List[int], rounding_func:Callable[[float],float]= None ) -> None:
    """
    Evaluates the best known solutions for Geismar et al. instances.

    Parameters:
        - instances:     instances to evaluate
        - capacities:    capacity values to evaluate with
        - lifespans:     lifespan values to evaluate with
        - rates:         production rates to evaluate with
        - rounding_func: rounding function
    """

    directory  = os.path.join( SOLUTION_DIRECTORY, 'geismar', 'best_known' )
    outputfile = os.path.join( OUTPUT_DIRECTORY, __tempfile )

    with open( outputfile, 'w' ) as f:
        for i in instances:
            instance = read_geismar_instance( i )

            for (Q,B,r) in product(capacities,lifespans,rates):
                solution = read_solution_for_geismar_instance( directory, i, Q, B, r )
                round_value = evaluate( instance, Q, B, r, solution, check_feasibility= True, rounding_func= rounding_func )

                f.write( f'{i};{Q};{B};{r};{round_value}\n' )

        print( f'values are written into "{outputfile}"' )

def evaluate_lacomme_et_al_solution_for_geismar_instance( i:int, Q:int, B:int, r:int, rep:int, rounding_func:Callable[[float],float]= None, check_feasibility:bool= True, print_reason:bool= False, print_solution:bool= False ) -> float:
    """
    Evaluates the solution for the corresponding Geismar et al. instance of Lacomme et al.

    Parameters:
        - rep: replication number (1,2,3,4,5)
        - ...
    """

    instance = read_geismar_instance( i )
    solution = read_solution_for_geismar_instance( os.path.join( SOLUTION_DIRECTORY, 'lacomme_et_al', f'rep{rep}' ), i, Q, B, r )
        
    return evaluate( instance, Q, B, r, solution, rounding_func, check_feasibility, print_reason, print_solution )

def evaluate_vns_solution_for_geismar_instance( i:int, Q:int, B:int, r:int, rounding_func:Callable[[float],float]= None, check_feasibility:bool= True, print_reason:bool= False, print_solution:bool= False ) -> float:
    """
    Evaluates the solution for the corresponding Geismar et al. instance of the variable neighborhood search of Horvath.
    """
    
    instance = read_geismar_instance( i )
    solution = read_solution_for_geismar_instance( os.path.join( SOLUTION_DIRECTORY, 'geismar', 'horvath_vns' ), i, Q, B, r )
        
    return evaluate( instance, Q, B, r, solution, rounding_func, check_feasibility, print_reason, print_solution )

def evaluate_vns_solution_for_canatasagun_instance( dem:int, loc:int, n:int, p:int, i:int, Q:int, B:int, r:int, rounding_func:Callable[[float],float]= None, check_feasibility:bool= True, print_reason:bool= False, print_solution:bool= False ):
    """
    Evaluates the solutions for Can Atasagun & Karaoglan instances of the variable neighborhood search of Horvath.

    Parameters:
        - ...
    """

    instance = read_canatasagun_instance( dem, loc, n, p, i )
    solution = read_solution_for_canatasagun_instance( os.path.join( SOLUTION_DIRECTORY, 'canatasagun', 'horvath_vns' ), dem, loc, n, p, i, Q, B, r )

    return evaluate( instance, Q, B, r, solution, rounding_func, check_feasibility, print_reason, print_solution )

if __name__ == '__main__':
    #rfunc = None
    #rfunc = floor
    rfunc = lambda x : round(x,2)

    # single-plant instances of Geismar et al.
    #evaluate_lacomme_et_al_solutions_for_geismar_instances( instances= [1,2,3,4,5,6], capacities= [300,600], lifespans= [300,600], rates= [1,2,3], check_feasibility= True )
    #evaluate_vns_solutions_for_geismar_instances( instances= [1,2,3,4,5,6], capacities= [300,600], lifespans= [300,600], rates= [1,2,3], rounding_func= rfunc )
    evaluate_bestknown_solutions_for_geismar_instances( instances= [1,2,3,4,5,6], capacities= [300,600], lifespans= [300,600], rates= [1,2,3], rounding_func= rfunc )

    # multi-plant instances of Canatasagun and Karaoglan
    CAK_NP = [ (n,p) for (n,p) in product([10],[2]) ] + [ (n,p) for (n,p) in product([20,30,40,50],[2,3]) ] + [ (n,p) for (n,p) in product([100],[3,4,5]) ]

    #evaluate_vns_solutions_for_canatasagun_instances( dems= [1,2], locs= [1,2,3], nps= CAK_NP, instances= [1,2,3], capacities= [300,600], lifespans= [300,600], rates= [1,2,3], rounding_func= rfunc )
