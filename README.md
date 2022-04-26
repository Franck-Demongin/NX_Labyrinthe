![hero](https://user-images.githubusercontent.com/54265936/165161197-500b5c1f-10ab-4022-b643-5320db9dad5e.png)

# NX_Labyrinthe

Blender addon to generate maze

<img src="https://img.shields.io/badge/Blender-3.1.0-green" /> <img src="https://img.shields.io/badge/Python-3.10-blue" /> <img src="https://img.shields.io/badge/Addon-1.0.0-orange" />
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)

The generated maze is "perfect"[^1], all cell could be visited and there is a way to throught it!

[^1]: "A perfect maze is a maze where any two cells can be joined by a unique path"
  ([Labirinthe.pdf](https://sancy.iut-clermont.uca.fr/~lafourcade/PAPERS/PDF/labyrinthe.pdf))
  
## Installation
Download ZIP archive for your blender version:

![Blender 3.0](https://github.com/Franck-Demongin/NX_Labyrinthe/releases/tag/v1.0.0)

![Blender 3.1](https://github.com/Franck-Demongin/NX_Labyrinthe/releases/tag/v1.1.0)

In Blender preferences:

- remove older version if needed
- install addon from Preferences > Add-ons > Install...  
- activate the addon

## Features

- [x] Choose X and Y cells number
- [x] Set cell size
- [x] Choose an orientation and this level of influence on the result
- [x] Add wall, height and thickness
- [x] Add corner, radius and number of segments
- [x] Add issues, create random issues
- [x] Update maze after this creation, wall, corner and issues
- [ ] Save maze in plein text
- [ ] Resolve maze      

## Exemples
In Object Mode _NX_Labyrinthe_ is located in the Sidebar (N) > NX_Tools

### Create maze

![initial_ui](https://user-images.githubusercontent.com/54265936/165274651-591e6739-f0bf-4871-913e-d1d96ab0c91f.png)

For your first try start with a little number of cells (under 10 or 15).  
Set a size of cell. The final length of the maze depends of this 2 options.  
Set wall height and thickness or let empty to generate only edges.  
To creae Entrance and Exit, select Issues

Press Create Labyrinthe to generate maze in your scene

Maze of 10x10 cells, with wall height and thickness:

![maze_10x10](https://user-images.githubusercontent.com/54265936/165280708-469876e6-1edd-420e-b680-e941c8eee8a6.png)

Maze corner with _Radius_ set to 0.05 and _Segments_ to 4:

![maze_corner](https://user-images.githubusercontent.com/54265936/165281644-2cbefd77-9848-4e35-bf25-3fa6ac7ba92a.png)

## Update maze
The maze must be recreated if you want to change the number of cells or the _Orientation_.  
In this case, click on _New maze_ to generate a new maze with these settings.
For the other options, _Cell Size_, _Wall_, _Corner_ and _Issues_, you can update the current maze without changing it.

## About the number of cells

As the addon uses _Geometry Node_ to remove the edges and create the final maze, there seems to be a limit beyond which it's really hard and extremely slow to go!  
I guess it depends on the hardware capabilities of the PC.  
The best result I can get with my laptop and its 16 GB of RAM (16 GB more with the Swap partition...) was a maze of 100x100 cells.
If your archieve a better result I will very happy to see that! :slightly_smiling_face:

![maze_100_100](https://user-images.githubusercontent.com/54265936/165292805-1f8da8df-314c-4583-bf77-08e3788891a6.png)

## More about maze algorithm in Python
The initial code was found on this site (https://allophysique.com), in this article : [Python Labyrinthe](https://allophysique.com/posts/python/python-labyrinthe/?fbclid=IwAR16AbrrbUUOEq4dz29jrjJtKWBoOiXBYpjHQGfOd-7hE5XiYik40jmlO-Q)

A big thank to this anonymous author!




