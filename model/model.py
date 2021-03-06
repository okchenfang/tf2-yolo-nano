import tensorflow as tf
from tensorflow.keras.layers import Input,UpSampling2D,Concatenate,Lambda
from .base_layers import conv1x1,conv3x3,PEP,EP,FCA,yolo_loss

def yoloNano(anchors,input_size=416,num_classes=1,include_attention=True):

    input_0 = Input(shape=(None, None, 3))
    input_gt = [Input(shape=(None, None, len(anchors) // 3, num_classes + 5)) for l in range(3)]

    x = conv3x3(filters=12,stride=(1,1))(input_0)
    x = conv3x3(filters=24,stride=(2,2))(x)
    x = PEP(filters=24, neck_filters=7)(x)
    x = EP(filters=70, stride=(2,2))(x)
    x = PEP(filters=70, neck_filters=25)(x)
    x = PEP(filters=70, neck_filters=24)(x)
    x = EP(filters=150, stride=(2, 2))(x)
    x = PEP(filters=150, neck_filters=56)(x)
    x = conv1x1(filters=150)(x)
    if include_attention:
        x = FCA(reduction_ratio=8)(x)
    x = PEP(filters=150, neck_filters=73)(x)
    x = PEP(filters=150, neck_filters=71)(x)
    x1 = PEP(filters=150, neck_filters=75)(x)
    x = EP(filters=325,stride=(2,2))(x1)
    x = PEP(filters=325,neck_filters=132)(x)
    x = PEP(filters=325,neck_filters=124)(x)
    x = PEP(filters=325,neck_filters=141)(x)
    x = PEP(filters=325,neck_filters=140)(x)
    x = PEP(filters=325,neck_filters=137)(x)
    x = PEP(filters=325,neck_filters=135)(x)
    x = PEP(filters=325, neck_filters=133)(x)
    x2 = PEP(filters=325, neck_filters=140)(x)
    x = EP(filters=545,stride=(2,2))(x2)
    x = PEP(filters=545, neck_filters=276)(x)
    x = conv1x1(filters=230)(x)
    x = EP(filters=489)(x)
    x = PEP(filters=469,neck_filters=213)(x)
    x3 = conv1x1(filters=189)(x)
    x = EP(filters=462)(x3)
    feature_13x13 = conv1x1(filters=3 * (num_classes + 5),bn=False)(x)
    x = conv1x1(filters=105)(x3)
    x = UpSampling2D()(x)
    x = Concatenate()([x,x2])
    x = PEP(filters=325,neck_filters=113)(x)
    x = PEP(filters=207,neck_filters=99)(x)
    x4 = conv1x1(filters=98)(x)
    x = EP(filters=183)(x4)
    feature_26x26 = conv1x1(filters=3 * (num_classes + 5),bn=False)(x)
    x = conv1x1(filters=47)(x4)
    x = UpSampling2D()(x)
    x = Concatenate()([x,x1])
    x = PEP(filters=122,neck_filters=58)(x)
    x = PEP(filters=87,neck_filters=52)(x)
    x = PEP(filters=93,neck_filters=47)(x)
    feature_52x52 = conv1x1(filters=3 * (num_classes + 5),bn=False)(x)

    loss = Lambda(yolo_loss, output_shape=(1,), name='yolo_loss',arguments={'anchors': anchors, 'num_classes': num_classes, 'ignore_thresh': 0.5})([feature_13x13,feature_26x26,feature_52x52, *input_gt])

    debug_model = tf.keras.Model(inputs=input_0,outputs=[feature_13x13,feature_26x26,feature_52x52])
    train_model = tf.keras.Model(inputs=[input_0,*input_gt],outputs=loss)
    return train_model,debug_model

# import numpy as np
# anchors = np.array([[6.,9.],[8.,13.],[11.,16.],[14.,22.],[17.,37.],[21.,26.],[29.,38.],[39.,62.],[79.,99.]],dtype='float32')
# model,_ = yoloNano(anchors,input_size=416,num_classes=1)
# model.summary()