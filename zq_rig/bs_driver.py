import pymel.core as pm
from maya_utils import NodeCreate

def create_WTDR_driver_fromJoint(baseJnt,ib=False):


    #baseJnt = pm.PyNode("shoulder_L")
    


    baseJntMatrix = baseJnt.getMatrix(worldSpace=1)
    childJnt = baseJnt.getChildren()[0]
    aimVector = childJnt.getTranslation(space="world") - baseJnt.getTranslation(space="world")
    aimVector.normalize()
    transform_aim = pm.dt.Vector()
    transform_front = pm.dt.Vector()
    transform_scale = childJnt.translate.get().length() * 0.3
    for i in range(3):

        vtr = pm.dt.Vector(baseJntMatrix[i][:3])
        vtr.normalize()
        zVtr = pm.dt.Vector(0,0,1)
        zDot = vtr*zVtr
        aDot = vtr * aimVector
        transform_front[i] = round(zDot,0)
        transform_aim[i] = round(aDot,0)



    baseName = baseJnt.name()

    baseGrp = pm.group(em=1,name=baseName + "_drive_GRP")
    baseGrp.setMatrix(baseJnt.getMatrix(worldSpace=1),worldSpace=1)

    pm.parentConstraint(baseJnt.getParent(),baseGrp,mo=1)

    posLoc = pm.spaceLocator(name=baseName + "_posLoc")
    posGrp = pm.group(posLoc,p=baseGrp,r=1,name=baseName + "_pos_grp")

    posGrp.translate.set(transform_aim*transform_scale)
    #posGrp.tx.set(baseJnt.getChildren()[0].translate.get().length() * 0.3)
    pm.parentConstraint(baseJnt,posLoc,mo=1)

    ###point Loc

    pointLoc = pm.spaceLocator(name=baseName + "_pointLoc")
    pm.parent(pointLoc,baseGrp,r=1)
    pointLoc.setLimited(18,1)
    pointLoc.setLimited(19,1)
    pointLoc.setLimit(18,0)
    pointLoc.setLimit(19,0)
    pm.pointConstraint(posLoc,pointLoc,mo=1)

    base_angloc = pm.spaceLocator(name=baseName+"_baes_Angloc")
    pm.parent(base_angloc,baseGrp,r=1)

    follow_angloc = pm.spaceLocator(name=baseName + "_follow_Angloc")
    pm.parent(follow_angloc,baseGrp,r=1)
    follow_angloc.translate.set(transform_aim*transform_scale)
    #follow_angloc.tx.set(baseJnt.getChildren()[0].translate.get().length() * 0.3)
    pm.parentConstraint(posLoc,follow_angloc,mo=1)


    state_angloc = pm.spaceLocator(name=baseName+"_state_Angloc")
    pm.parent(state_angloc,baseGrp,r=1)
    state_angloc.translate.set(transform_aim*transform_scale)
    #state_angloc.tx.set(baseJnt.getChildren()[0].translate.get().length() * 0.3)

    bridge = pm.group(em=1,p=baseGrp,r=1,n=baseName+"_bridge")
    bridgeAttrList = [
        {"__":"current_length"},
        {"driver_value":0},
        {"_______":"angle_base"},
        {"angle_base":0},
        {"angle_frontUp":[45,1,89]},
        {"angle_backUp":[135,91,179]},
        {"angle_frontBottom":[45,1,89]},
        {"angle_backBottom":[135,91,179]},
        {"_________":"Interval_sevalue"},
        {"Interval_sevalue":0},
        {"__________":"SDK_driver"},
        {"front_driver":0},
        {"up_driver":0},
        {"back_driver":0},
        {"bottom_driver":0},
        {"frontUp_driver":0},
        {"backUp_driver":0},
        {"frontBottom_driver":0},
        {"backBottom_driver":0}
    ]
    for i in bridgeAttrList:
        a = i.keys()[0]
        v = i.values()[0]
        if type(v)==str:
            bridge.addAttr(a,at="enum",en=v,k=1)
        elif type(v) == list:
            bridge.addAttr(a,dv=v[0],min=v[1],max=v[2],k=1)
        else:
            bridge.addAttr(a,k=1)


    baseangle_loc = pm.spaceLocator(name=baseName+"_baseangle_loc")
    pm.parent(baseangle_loc,baseGrp,r=1)

    basefrontangle_loc = pm.spaceLocator(name=baseName+"_basefrontangle_loc")
    pm.parent(basefrontangle_loc,baseGrp,r=1)
    basefrontangle_loc.translate.set(transform_front*transform_scale)

    aim_abs = abs(transform_aim)
    aim_axisIndex = aim_abs.index(max(aim_abs))[0]

    front_abs = abs(transform_front)
    front_axisIndex = front_abs.index(max(front_abs))[0]
    translateList = [pointLoc.tx,pointLoc.ty,pointLoc.tz]
    pointLoc_front_back_translate = translateList[front_axisIndex]
    
    pointLoc_up_botton_translate = translateList[3-(aim_axisIndex + front_axisIndex)]

    
    #basefrontangle_loc.tz.set(baseJnt.getChildren()[0].translate.get().length() * 0.3)

    ### Interval sevalue

    yselection = NodeCreate.conditionCreate(pointLoc_up_botton_translate,0,3,[3,0,0],[1,1,1],name=baseName+"_Y_selection_condition")
    zselection = NodeCreate.conditionCreate(pointLoc_front_back_translate,0,3,[6,0,0],[2,1,1],name=baseName+"_Z_selection_condition")
    yliner = NodeCreate.conditionCreate(pointLoc_up_botton_translate,0,0,[1,0,0],[0,1,1],name=baseName+"_Y_liner_condition")
    zliner = NodeCreate.conditionCreate(pointLoc_front_back_translate,0,0,[0.5,0,0],[0,1,1],name=baseName+"_Z_liner_condition")
    multi_pma = NodeCreate.plusMinusCreate(d1=[yselection.outColor.outColorR,zselection.outColor.outColorR,yliner.outColor.outColorR,zliner.outColor.outColorR],name=baseName+"_multi_pma")
    multi_pma.output1D.connect(bridge.Interval_sevalue)

    ###  Angle base 
    angle_pma_2 = NodeCreate.plusMinusCreate(d3=[pointLoc.worldPosition,baseangle_loc.worldPosition],op=2,name=baseName+"_angle01_pma")
    angle_pma_1 = NodeCreate.plusMinusCreate(d3=[basefrontangle_loc.worldPosition,baseangle_loc.worldPosition],op=2,name=baseName+"_angle02_pma")
    angleVector = NodeCreate.angleBetweenCreate(vector1=angle_pma_1.output3D,vector2=angle_pma_2.output3D,name=baseName+"_angleBt")
    angleVector.angle.connect(bridge.angle_base)

    ###   drive value
    angle_pma_1 = NodeCreate.plusMinusCreate(d3=[follow_angloc.translate,base_angloc.translate],op=2,name=baseName+"_anglePMA01")
    angle_pma_2 = NodeCreate.plusMinusCreate(d3=[state_angloc.translate,base_angloc.translate],op=2,name=baseName+"_anglePMA02")
    angleVector = NodeCreate.angleBetweenCreate(vector1=angle_pma_1.output3D,vector2=angle_pma_2.output3D,name=baseName+"_angle_AB_Bt")
    angleValueMD = NodeCreate.multiDiviCreate(input1X=angleVector.angle,input2X=90,operation=2,name=baseName+"_angValueMD")
    angleValue_Clamp = NodeCreate.defaultCreate(type="clamp",inputR=angleValueMD.outputX,max=[1,1,1])
    angleValue_Clamp.outputR.connect(bridge.driver_value)

    ### backBottom Driver

    interval4_condition = NodeCreate.conditionCreate(bridge.Interval_sevalue,3,0,[1,0,0],[0,1,1],name=baseName+"_outputInterval04_condition")
    backBtmSdk01_condition = NodeCreate.conditionCreate(interval4_condition.outColorR,1,0,[1,0,0],[0,1,1],name=baseName+"_backBottomsdk_sdk01_condition")
    backBtm_anglesdk_pma = NodeCreate.plusMinusCreate(d2=[[bridge.angle_backBottom,0],[90,0]],d3=[[180,bridge.angle_base,180],[bridge.angle_base,90,bridge.angle_backBottom]],op=2,name=baseName+"_backBottom_anglesdk_pma")
    baskBtm_anblesdk_condition = NodeCreate.conditionCreate(bridge.angle_base,bridge.angle_backBottom,2,
                                    [backBtm_anglesdk_pma.output3Dx,backBtm_anglesdk_pma.output3Dz,0,],
                                    [backBtm_anglesdk_pma.output3Dy,backBtm_anglesdk_pma.output2Dx,1],name=baseName+"_backBottom_anglesdk_condition")
    backBtmsdk01_md = NodeCreate.multiDiviCreate(input1X=baskBtm_anblesdk_condition.outColorR,input2X=baskBtm_anblesdk_condition.outColorG,operation=2,name=baseName+"_backBottomsdk_sdk01_md")
    backBtmSdkOut_md = NodeCreate.multiDiviCreate(input1X=backBtmsdk01_md.outputX,input2X=backBtmSdk01_condition.outColorR,operation=1,name=baseName + "_backBottom_anglesdkout_md")
    backBtmsdk02_md = NodeCreate.multiDiviCreate(input1X=bridge.driver_value,input2X=backBtmSdkOut_md.outputX,operation=1,name=baseName + "_backBottomsdk_sdk02_md")
    backBtmsdk02_md.outputX.connect(bridge.backBottom_driver)

    ### frontBottom Driver

    interval3_condition = NodeCreate.conditionCreate(bridge.Interval_sevalue,7,0,[1,0,0],[0,1,1],name=baseName+"_outputInterval03_condition")
    frontBtmSdk01_condition = NodeCreate.conditionCreate(interval3_condition.outColorR,1,0,[1,0,0],[0,1,1],name=baseName+"_frontBottom_sdk01_condition")

    frontBtm_anglesdk_pma = NodeCreate.plusMinusCreate(d3=[[90,0,90],[bridge.angle_base,0,bridge.angle_frontBottom]],op=2,name=baseName + "_frontBottom_anglesdk_pma")
    frontBtm_anblesdk_condition = NodeCreate.conditionCreate(
                                                        bridge.angle_base,bridge.angle_frontBottom,2,
                                                        [frontBtm_anglesdk_pma.output3Dx,frontBtm_anglesdk_pma.output3Dz,0],
                                                        [bridge.angle_base,bridge.angle_frontBottom,1],name=baseName + "_frontBottom_anglesdk_condition"
                                                    )

    frontBtm_sdk01_md = NodeCreate.multiDiviCreate(input1X=frontBtm_anblesdk_condition.outColorR,input2X=frontBtm_anblesdk_condition.outColorG,operation=2,name=baseName + "_frontBottom_sdk01_md")
    frontBtm_anglesdkout_md = NodeCreate.multiDiviCreate(input1X=frontBtm_sdk01_md.outputX,input2X=frontBtmSdk01_condition.outColorR,operation=1,name="_frontBottom_anglesdkout_md")

    frontBtm_sdk02_md = NodeCreate.multiDiviCreate(input1X=bridge.driver_value,input2X=frontBtm_anglesdkout_md.outputX,operation=1,name="_frontBottom_sdk02_md")
    frontBtm_sdk02_md.outputX.connect(bridge.frontBottom_driver)

    #### front driver

    interval1_condition = NodeCreate.conditionCreate(bridge.Interval_sevalue,9,0,[1,0,0],[0,1,1],name=baseName+"_outputInterval01_condition")
    interval_axis_PosZ_condition = NodeCreate.conditionCreate(bridge.Interval_sevalue,10,0,[1,0,0],[0,1,1],name=baseName+"_outputInterval_axis_PosZ_conditon")

    frontsdk01_pma = NodeCreate.plusMinusCreate(d1=[interval1_condition.outColorR,interval_axis_PosZ_condition.outColorR,interval3_condition.outColorR],name=baseName + "__front_sdk01_pma")
    frontsdk02_pma = NodeCreate.plusMinusCreate(d2=[[90,0],[bridge.angle_base,0]],op=2,name=baseName + "_front_sdk02_pma")
    frontsdk01_md = NodeCreate.multiDiviCreate(input1X=frontsdk02_pma.output2Dx,input2X=90,operation=2,name=baseName+"_front_sdk01_md")

    frontsdk01_condition = NodeCreate.conditionCreate(frontsdk01_pma.output1D,1,0,[frontsdk01_md.outputX,0,0],[0,1,1],name=baseName+"_front_sdk01_condition")
    y_state_condition = NodeCreate.conditionCreate(pointLoc_front_back_translate,0,3,[bridge.driver_value,0,0],[0,bridge.driver_value,1],name=baseName + "_Y_state_conditon")

    frontsdk02_md = NodeCreate.multiDiviCreate(input1X=frontsdk01_condition.outColorR,input2X=y_state_condition.outColorR,operation=1,name=baseName + "_front_sdk02_md")
    frontsdk02_md.outputX.connect(bridge.front_driver)

    #### back driver

    interval2_condition = NodeCreate.conditionCreate(bridge.Interval_sevalue,5,0,[1,0,0],[0,1,1],name=baseName+"_outputInterval02_condition")
    interval_axis_negZ_condition = NodeCreate.conditionCreate(bridge.Interval_sevalue,6,0,[1,0,0],[0,1,1],name=baseName+"_outputInterval_axis_negZ_conditon")

    backsdk01_pma = NodeCreate.plusMinusCreate(d1=[interval2_condition.outColorR,interval4_condition.outColorR,interval_axis_negZ_condition.outColorR],name=baseName+"_back_sdk01_pma")
    backsdk02_pma = NodeCreate.plusMinusCreate(d2=[[bridge.angle_base,0],[90,0]],op=2,name=baseName+"_back_sdk02_pma")

    backsdk01_md = NodeCreate.multiDiviCreate(input1X=backsdk02_pma.output2Dx,input2X=90,operation=2,name=baseName+"_back_sdk01_md")

    backsdk01_condition = NodeCreate.conditionCreate(backsdk01_pma.output1D,1,0,[backsdk01_md.outputX,0,0],[0,1,1],name=baseName+"_back_sdk01_condition")

    backsdk02_md = NodeCreate.multiDiviCreate(input1X=backsdk01_condition.outColorR,input2X=y_state_condition.outColorG,name=baseName+"_back_sdk02_md")
    backsdk02_md.outputX.connect(bridge.back_driver)

    ### up driver
    interval_axis_PosY_condition = NodeCreate.conditionCreate(bridge.Interval_sevalue,9.5,0,[1,0,0],[0,1,1],name=baseName+"_outputInterval_axis_PosY_conditon")
    upsdk01_pma = NodeCreate.plusMinusCreate(d1=[interval1_condition.outColorR,interval2_condition.outColorR,interval_axis_PosY_condition.outColorR],name=baseName+"_up_sdk01_pma")

    upsdk02_pma = NodeCreate.plusMinusCreate(d2=[[180,0],[bridge.angle_base,0]],op=2,name=baseName+"_up_sdk02_pma")
    front_anglesdk_codition = NodeCreate.conditionCreate(bridge.angle_base,90,2,[upsdk02_pma.output2Dx,0,0],[bridge.angle_base,1,1],name=baseName+"_front_anglesdk_condition")
    upsdk01_md = NodeCreate.multiDiviCreate(input1X=front_anglesdk_codition.outColorR,input2X=90,operation=2,name=baseName+"_up_sdk01_md")
    upsdk01_condition = NodeCreate.conditionCreate(upsdk01_pma.output1D,1,0,[upsdk01_md.outputX,0,0],[0,1,1],name=baseName+"_up_sdk01_condition")

    z_state_condition = NodeCreate.conditionCreate(pointLoc_up_botton_translate,0,3,[bridge.driver_value,0,0],[0,bridge.driver_value,0],name=baseName+"_Z_state_conditon")
    upsdk02_md = NodeCreate.multiDiviCreate(input1X=upsdk01_condition.outColorR,input2X=z_state_condition.outColorR,name=baseName+"_up_sdk02_md")
    upsdk02_md.outputX.connect(bridge.up_driver)

    ###  bottom driver

    interval_axis_negY_condition = NodeCreate.conditionCreate(bridge.Interval_sevalue,7.5,0,[1,0,0],[0,1,1],name=baseName+"_outputInterval_axis_negZ_conditon")
    bottomsdk01_pma = NodeCreate.plusMinusCreate(d1=[interval3_condition.outColorR,interval4_condition.outColorR,interval_axis_negY_condition.outColorR],name="_bottom_sdk01_pma")

    bottomsdk02_pma = NodeCreate.plusMinusCreate(d2=[[180,0],[bridge.angle_base,0]],op=2,name=baseName+"_bottom_sdk02_pma")
    bottom_anglesdk_codition = NodeCreate.conditionCreate(bridge.angle_base,90,2,[bottomsdk02_pma.output2Dx,0,0],[bridge.angle_base,1,1],name=baseName+"_bottom_anglesdk_condition")

    bottomsdk01_md = NodeCreate.multiDiviCreate(input1X=bottom_anglesdk_codition.outColorR,input2X=90,operation=2,name=baseName+"_botton_sdk01_md")
    bottonsdk01_codition = NodeCreate.conditionCreate(bottomsdk01_pma.output1D,1,0,[bottomsdk01_md.outputX,0,0],[0,1,1],name=baseName+"_bottom_sdk01_condition")

    bottomsdk02_md = NodeCreate.multiDiviCreate(input1X=bottonsdk01_codition.outColorR,input2X=z_state_condition.outColorG,name=baseName+"_bottom_sdk02_md")
    bottomsdk02_md.outputX.connect(bridge.bottom_driver)

    ###front up driver

    frontUpsdk01_condition = NodeCreate.conditionCreate(interval1_condition.outColorR,1,0,[1,0,0],[0,1,1],name=baseName+"_frontUp_sdk01_condition")

    frontUp_anglesdk_pma = NodeCreate.plusMinusCreate(d3=[[90,0,90],[bridge.angle_base,0,bridge.angle_frontUp]],op=2,name=baseName+"_frontUp_anglesdk_pma")
    frontUp_anglesdk_condition = NodeCreate.conditionCreate(bridge.angle_base,bridge.angle_frontUp,2,
                                            [frontUp_anglesdk_pma.output3Dx,frontUp_anglesdk_pma.output3Dz,0],
                                            [bridge.angle_base,bridge.angle_frontUp,1],name=baseName+"_frontUp_anglesdk_condition")

    frontUpsdk01_md = NodeCreate.multiDiviCreate(input1X=frontUp_anglesdk_condition.outColorR,input2X=frontUp_anglesdk_condition.outColorG,operation=2,name=baseName+"_frontUp_sdk01_md")
    frontUp_anglesdkout_md = NodeCreate.multiDiviCreate(input1X=frontUpsdk01_md.outputX,input2X=frontUpsdk01_condition.outColorR,name=baseName+"_frontUp_anglesdkout_md")

    frontUpsdk02_md = NodeCreate.multiDiviCreate(input1X=bridge.driver_value,input2X=frontUp_anglesdkout_md.outputX,name=baseName+"_frontUp_sdk02_md")
    frontUpsdk02_md.outputX.connect(bridge.frontUp_driver)

    #### back up driver

    backUpsdk01_condition = NodeCreate.conditionCreate(interval2_condition.outColorR,1,0,[1,0,0],[0,1,1],name=baseName+"_backUp_sdk01_condition")
    frontUp_anglesdk_pma = NodeCreate.plusMinusCreate(d2=[[bridge.angle_backUp,0],[90,0]],
                                                        d3=[[180,bridge.angle_base,180],[bridge.angle_base,90,bridge.angle_backUp]],op=2,name=baseName+"_backUp_anglesdk_pma")

    backup_anglesdk_condition = NodeCreate.conditionCreate(bridge.angle_base,bridge.angle_backUp,2,[frontUp_anglesdk_pma.output3Dx,frontUp_anglesdk_pma.output3Dz,0],
                                                                                                    [frontUp_anglesdk_pma.output3Dy,frontUp_anglesdk_pma.output2Dx,1],name=baseName+"_backUp_anglesdk_condition")
    backUpsdk01_md = NodeCreate.multiDiviCreate(input1X=backup_anglesdk_condition.outColorR,input2X=backup_anglesdk_condition.outColorG,operation=2,name=baseName+"_backUp_sdk01_md")
    backUP_anglesdkout_md = NodeCreate.multiDiviCreate(input1X=backUpsdk01_md.outputX,input2X=backUpsdk01_condition.outColorR,name="_backUp_anglesdkout_md")
    backUpsdk02_md = NodeCreate.multiDiviCreate(input1X=bridge.driver_value,input2X=backUP_anglesdkout_md.outputX,name=baseName+"_backUp_sdk02_md")
    backUpsdk02_md.outputX.connect(bridge.backUp_driver)


    ### fixed   frontUp backUp frontBottom backBottom

    if ib:
        fix_backUp_pma = NodeCreate.plusMinusCreate(d1=[1,backUP_anglesdkout_md.outputX],op=2,name=baseName+"_fix_backUp_pma")

        fix_frontUp_pma = NodeCreate.plusMinusCreate(d1=[1,frontUp_anglesdkout_md.outputX],op=2,name=baseName+"_fix_frontUp_pma")
        fix_backBottom_pma = NodeCreate.plusMinusCreate(d1=[1,backBtmSdkOut_md.outputX],op=2,name=baseName+"_fix_backBottom_pma")
        fix_frontBottom_pma = NodeCreate.plusMinusCreate(d1=[1,frontBtm_anglesdkout_md.outputX],op=2,name=baseName+"_fix_frontBottom_pma")

        fix_up_md = NodeCreate.multiDiviCreate(input1X=fix_backUp_pma.output1D,input2X=fix_frontUp_pma.output1D,name=baseName+"_fix_up_md")
        fix_bottom_md = NodeCreate.multiDiviCreate(input1X=fix_backBottom_pma.output1D,input2X=fix_frontBottom_pma.output1D,name=baseName+"_fix_bottom_md")
        fix_front_md = NodeCreate.multiDiviCreate(input1X=fix_frontBottom_pma.output1D,input2X=fix_frontUp_pma.output1D,name=baseName+"_fix_front_md")
        fix_back_md = NodeCreate.multiDiviCreate(input1X=fix_backBottom_pma.output1D,input2X=fix_backUp_pma.output1D,name=baseName+"_fix_back_md")

        fit_up_out_md = NodeCreate.multiDiviCreate(input1X=fix_up_md.outputX,input2X=upsdk02_md.outputX,name=baseName+"_fit_up_out_md")
        fit_up_out_md.outputX.connect(bridge.up_driver,f=1)

        fit_bottom_out_md = NodeCreate.multiDiviCreate(input1X=fix_bottom_md.outputX,input2X=bottomsdk02_md.outputX,name=baseName+"_fit_bottom_out_md")
        fit_bottom_out_md.outputX.connect(bridge.bottom_driver,f=1)

        fit_front_out_md = NodeCreate.multiDiviCreate(input1X=fix_front_md.outputX,input2X=frontsdk02_md.outputX,name=baseName+"_fit_front_out_md")
        fit_front_out_md.outputX.connect(bridge.front_driver,f=1)

        fit_back_out_md = NodeCreate.multiDiviCreate(input1X=fix_back_md.outputX,input2X=backsdk02_md.outputX,name=baseName+"_fit_back_out_md")
        fit_back_out_md.outputX.connect(bridge.back_driver,f=1)



    frontValue = sum(basefrontangle_loc.translate.get())
    if frontValue < 0:
        yselection.operation.set(5)
        zselection.operation.set(5)
        zselection.secondTerm.set(0.00001)
        yselection.secondTerm.set(0.00001)

        z_state_condition.operation.set(5)
        y_state_condition.operation.set(5)
    else:
        zselection.secondTerm.set(-0.00001)
        yselection.secondTerm.set(-0.00001)


    BS_Node = pm.PyNode("BodyBS")
    BS_aliase_dict = {}
    for i in BS_Node.listAliases():
        BS_aliase_dict[i[0]] = i[1]

    if BS_aliase_dict.has_key(baseJnt.name() + "_0_n90_0"):
        bridge.up_driver.connect(BS_aliase_dict[baseJnt.name() + "_0_n90_0"],f=1)
    if BS_aliase_dict.has_key(baseJnt.name() + "_0_90_0"):
        bridge.bottom_driver.connect(BS_aliase_dict[baseJnt.name() + "_0_90_0"],f=1)
    if BS_aliase_dict.has_key(baseJnt.name() + "_0_0_90"):
        bridge.front_driver.connect(BS_aliase_dict[baseJnt.name() + "_0_0_90"],f=1)
    if BS_aliase_dict.has_key(baseJnt.name() + "_0_0_n90"):
        bridge.back_driver.connect(BS_aliase_dict[baseJnt.name() + "_0_0_n90"],f=1)
    if BS_aliase_dict.has_key(baseJnt.name() + "_0_90_45"):
        bridge.frontBottom_driver.connect(BS_aliase_dict[baseJnt.name() + "_0_90_45"],f=1)
    if BS_aliase_dict.has_key(baseJnt.name() + "_0_n90_45"):
        bridge.frontUp_driver.connect(BS_aliase_dict[baseJnt.name() + "_0_n90_45"],f=1)
    if BS_aliase_dict.has_key(baseJnt.name() + "_0_90_n45"):
        bridge.backBottom_driver.connect(BS_aliase_dict[baseJnt.name() + "_0_90_n45"],f=1)
    if BS_aliase_dict.has_key(baseJnt.name() + "_0_n90_n45"):
        bridge.backUp_driver.connect(BS_aliase_dict[baseJnt.name() + "_0_n90_n45"],f=1)

    # bridge.bottom_driver.connect(bs.weight.Shoulder_L_0_90_0,f=1)
    # bridge.front_driver.connect(bs.weight.Shoulder_L_0_0_90,f=1)
    # bridge.back_driver.connect(bs.weight.Shoulder_L_0_0_n90,f=1)
    # bridge.frontBottom_driver.connect(bs.weight.Shoulder_L_0_90_45,f=1)
    # bridge.frontUp_driver.connect(bs.weight.Shoulder_L_0_n90_45,f=1)
    # bridge.backBottom_driver.connect(bs.weight.Shoulder_L_0_90_n45,f=1)
    # bridge.backUp_driver.connect(bs.weight.Shoulder_L_0_n90_n45,f=1)
    # return bridge


def create_ball_driver_fromJoint(joint,fd=8):
    pass





if __name__ == "__main__":

    create_WTDR_driver_fromJoint(pm.selected()[0])