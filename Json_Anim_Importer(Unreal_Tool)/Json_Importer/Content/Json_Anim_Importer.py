import unreal
import json
import os


#Main function, get the bindings from Unreal level Sequence
def import_json(folder_path):
    import_bindings = []
    assets = unreal.EditorUtilityLibrary.get_selected_assets()

    #get all the binding actor with Sequencer
    for asset in assets:
        bindings = asset.get_bindings()

        for binding in bindings:
            binding_name = binding.get_name()
            print(binding_name)
            import_bindings.append(binding)
    
    
    set_keys(import_bindings,folder_path)

# set key frame for the skeleton mesh in Unreal
def set_keys(bindings,folder_path):
    from os import listdir
    from os.path import isfile, join
    import ast

    #get all frame_#.json files
    files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]

    step_num= len(files)

    #exec key frame function
    with unreal.ScopedSlowTask(step_num,'Hold on...') as dialogTask:
        dialogTask.make_dialog(True)

        for file in files:
            frame_number = int((str(file).replace('frame_','')).replace('.json',''))
            print(frame_number)
            one_frame_dict = None

            #read json file content
            with open(folder_path+'/'+file, "r") as f:
                one_frame_dict = ast.literal_eval(f.read())
            
            namespace = get_name_space(one_frame_dict)
            
            # traverse each channel by structure of level sequence 
            for binding in bindings:
                tracks = binding.get_tracks()
                for track in tracks:
                    track_name = track.get_display_name()
                    
                    #filte correct track
                    if (track_name == "FKControlRig"):
                        sections = track.get_sections()
                        for section in sections:
                            channels = section.get_channels()
                            
                            for channel in channels:

                                #get input by the Unreal naming convension
                                channel_name = ("{0}:{1}".format(namespace,str(channel.channel_name))) 
                                channel_front_name, channel_end_name= channel_name.split(".",1)
                                channel_front_name = channel_front_name.replace("_CONTROL","")
                                one_frame_dict_keys = list(one_frame_dict.keys())


                                #Because of the Axis system in Maya and Unreal is different, add the magic number, do not have enough time, will optimiz it later
                                if(channel_end_name == "Location.X"):
                                    channel_end_name = ("tx" )
                                    if(channel_front_name in one_frame_dict_keys):
                                        unreal_add_key(channel, unreal.FrameNumber(frame_number), (one_frame_dict[channel_front_name][channel_end_name]))
                                elif(channel_end_name == "Location.Y"):
                                    channel_end_name = ("ty" )
                                    if(channel_front_name in one_frame_dict_keys):
                                        unreal_add_key(channel, unreal.FrameNumber(frame_number), -(one_frame_dict[channel_front_name][channel_end_name]))
                                elif(channel_end_name == "Location.Z"):
                                    channel_end_name = ("tz" )
                                    if(channel_front_name in one_frame_dict_keys):
                                        unreal_add_key(channel, unreal.FrameNumber(frame_number), (one_frame_dict[channel_front_name][channel_end_name]))
                                elif(channel_end_name == "Rotation.X"):
                                    channel_end_name = ("rx" )
                                    if(channel_front_name in one_frame_dict_keys):
                                        unreal_add_key(channel, unreal.FrameNumber(frame_number), (one_frame_dict[channel_front_name][channel_end_name]))
                                elif(channel_end_name == "Rotation.Y"):
                                    channel_end_name = ("ry" )
                                    if(channel_front_name in one_frame_dict_keys):
                                        unreal_add_key(channel, unreal.FrameNumber(frame_number), -(one_frame_dict[channel_front_name][channel_end_name]))
                                elif(channel_end_name == "Rotation.Z"):
                                    channel_end_name = ("rz" )
                                    if(channel_front_name in one_frame_dict_keys):
                                        unreal_add_key(channel, unreal.FrameNumber(frame_number), -(one_frame_dict[channel_front_name][channel_end_name]))
                                elif(channel_end_name == "Scale.X"):
                                    channel_end_name = ("sx" )
                                    if(channel_front_name in one_frame_dict_keys):
                                        unreal_add_key(channel, unreal.FrameNumber(frame_number), (one_frame_dict[channel_front_name][channel_end_name]))
                                elif(channel_end_name == "Scale.Y"):
                                    channel_end_name = ("sy" )
                                    if(channel_front_name in one_frame_dict_keys):
                                        unreal_add_key(channel, unreal.FrameNumber(frame_number), (one_frame_dict[channel_front_name][channel_end_name]))
                                elif(channel_end_name == "Scale.Z"):
                                    channel_end_name = ("sz" )
                                    if(channel_front_name in one_frame_dict_keys):
                                        unreal_add_key(channel, unreal.FrameNumber(frame_number), (one_frame_dict[channel_front_name][channel_end_name]))
                             
                                dialogTask.enter_progress_frame(1,'Uploading '+ str(file) + " "+str(channel_name))
            
#add key for channel
def unreal_add_key(channel, time, newvalue):
    channel.add_key(time, newvalue)

#get the name space from json file
def get_name_space(dict):
    one_key = list(dict.keys())[0]
    namespace = one_key.split(":")[0]
    return(namespace)


