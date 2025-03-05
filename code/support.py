import pygame
from os import walk
from random import randint

def import_folder(path):
    surface_list = []
    for folder_name, sub_folders, img_files in walk(path):
        for image_name in img_files:
            full_path = path + '/' + image_name
            image_surf = pygame.image.load(full_path).convert_alpha()
            # add image surface to surface list
            surface_list.append(image_surf)
    return surface_list

def import_list(path):
    surface_dic = {}
    for folder_name, sub_folders, img_files in walk(path):
        for image_name in img_files:
            full_path = path + '/' + image_name
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dic[image_name.split('.')[0]] = image_surf
    return surface_dic
#
# def import_list(path):
#     surface_dic = {}
#     for folder_name, sub_folders, img_files in walk(path):
#         for image_name in img_files:
#             full_path = path + '/' + image_name
#             image_surf = pygame.image.load(full_path).convert_alpha()
#             surface_dic[image_name.split('.')[0]] = image_surf
#     return surface_dic
# def blit_text(abc,file,iters,offset):

    # display_surface.blit(pygame.transform.scale_by(list[chr(num)],2),(50,50))
    # var = put text in here
    # for char in var:
    #     blit[char]
# PROFILING CODE
#self.profiler_info = [0,0]  # in init method


# self.profile = cProfile.Profile()
# self.profile.enable()
# self.profile.disable()
# results = pstats.Stats(self.profile)
# results.sort_stats(pstats.SortKey.TIME)
# for key, value in results.stats.items():
#     self.profiler_info[0] += value[2]
# self.profiler_info[1] += 1
# keys = pygame.key.get_pressed()
# if keys[pygame.K_ESCAPE]:
#     print(self.profiler_info[0])
#     print(self.profiler_info[0] / self.profiler_info[1])
#     exit()