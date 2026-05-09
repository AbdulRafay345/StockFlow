import heapq

GRID_SIZE = 20          # The warehouse is a 20×20 tile grid.
SHELF_COLUMNS = [2, 5, 8, 11, 14, 17]   # x-coordinates that contain shelves.
SHELF_ROW_MIN = 2       # Shelves start at this row.
SHELF_ROW_MAX = 17      # Shelves end at this row (inclusive).

# The four cardinal directions a picker can move (no diagonals).
CARDINAL_DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]


# ---------------------------------------------------------------------------
# Grid layout helpers
# ---------------------------------------------------------------------------

def is_shelf(x: int, y: int) -> bool:
    return x in SHELF_COLUMNS and SHELF_ROW_MIN <= y <= SHELF_ROW_MAX


def is_walkable(x: int, y: int) -> bool:
    in_bounds = 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE
    return in_bounds and not is_shelf(x, y)


def get_walkable_neighbors(x: int, y: int) -> list:
    return [
        (x + dx, y + dy)
        for dx, dy in CARDINAL_DIRECTIONS
        if is_walkable(x + dx, y + dy)
    ]


def manhattan_distance(point_a: tuple, point_b: tuple) -> int:
    return abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1])


# ---------------------------------------------------------------------------
# Pathfinding — A* search
# ---------------------------------------------------------------------------

def find_path_to_item(start: tuple, item_location: tuple) -> list:

    # Decide where the picker should stop.
    if is_walkable(*item_location):
        # Item is in an aisle — walk right to it.
        candidate_stops = [item_location]
    else:
        # Item is on a shelf — stop at any adjacent aisle tile.
        candidate_stops = [
            (item_location[0] + dx, item_location[1] + dy)
            for dx, dy in CARDINAL_DIRECTIONS
            if is_walkable(item_location[0] + dx, item_location[1] + dy)
        ]

    if not candidate_stops:
        return []   # Item is completely surrounded by shelves — unreachable.

    # ── A* search ─────────────────────────────────────────────────────────
    # frontier  : min-heap of (priority, tile)
    # came_from : maps each visited tile to the tile we arrived from
    # cost      : cheapest known path length (in steps) to each visited tile
    # ──────────────────────────────────────────────────────────────────────
    frontier  = [(0, start)]
    came_from = {start: None}
    cost      = {start: 0}
    destination = None

    while frontier:
        _, current = heapq.heappop(frontier)

        if current in candidate_stops:
            destination = current
            break   # Found the nearest stop — no need to keep searching.

        for neighbor in get_walkable_neighbors(*current):
            new_cost = cost[current] + 1
            if neighbor not in cost or new_cost < cost[neighbor]:
                cost[neighbor] = new_cost
                # Heuristic: distance to the nearest candidate stop.
                heuristic = min(manhattan_distance(neighbor, stop) for stop in candidate_stops)
                heapq.heappush(frontier, (new_cost + heuristic, neighbor))
                came_from[neighbor] = current

    if destination is None:
        return []   # A* exhausted the grid without finding a stop tile.

    # Reconstruct the path by walking backwards through came_from.
    path, tile = [], destination
    while tile is not None:
        path.append(tile)
        tile = came_from[tile]
    path.reverse()
    return path


# ---------------------------------------------------------------------------
# Route optimisation — nearest-neighbour TSP heuristic
# ---------------------------------------------------------------------------

def get_optimal_pick_path(start: tuple, items: list):
    
    if not items:
        return [], {}

    # Group items that share the same shelf location so they can be picked
    # in a single stop.
    items_by_location = {}
    for item in items:
        loc = (item.loc_x, item.loc_y)
        items_by_location.setdefault(loc, []).append(item.name)

    current_pos = start
    total_path  = [start]
    pick_events = {}
    remaining   = dict(items_by_location)   # locations we still need to visit

    while remaining:
        # Find the nearest unvisited item location by actual path length.
        nearest_path = None
        nearest_loc  = None

        for target_loc in remaining:
            # Quick-check: are we already standing right next to this item?
            already_adjacent = (
                target_loc == current_pos or
                (manhattan_distance(current_pos, target_loc) == 1 and not is_walkable(*target_loc))
            )

            if already_adjacent:
                path_to_target = [current_pos]
            else:
                path_to_target = find_path_to_item(current_pos, target_loc)

            if path_to_target:
                if nearest_path is None or len(path_to_target) < len(nearest_path):
                    nearest_path = path_to_target
                    nearest_loc  = target_loc

        if nearest_path is None:
            break   # Remaining items are all unreachable — stop here.

        # Append the new steps (skip index 0 — that tile is where we already are).
        if len(nearest_path) > 1:
            total_path.extend(nearest_path[1:])

        current_pos = nearest_path[-1]
        pick_events.setdefault(current_pos, []).extend(remaining[nearest_loc])
        del remaining[nearest_loc]

    # Return to dispatch once all items have been collected.
    if current_pos != start:
        return_path = find_path_to_item(current_pos, start)
        if return_path and len(return_path) > 1:
            total_path.extend(return_path[1:])

    return total_path, pick_events