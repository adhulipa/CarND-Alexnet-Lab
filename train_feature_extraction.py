import pickle
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from alexnet import AlexNet

# Load traffic signs data.
training_file = 'train.p'
with open(training_file, mode='rb') as f:
    data = pickle.load(f)
X_data, y_data = data['features'], data['labels']
nb_classes = 43

# Split data into training and validation sets.
X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.33)

# Define placeholders and resize operation.
x = tf.placeholder(tf.float32, (None,32,32,3))
resized = tf.image.resize_images(x, (227,227))

# pass placeholder as first argument to `AlexNet`.
fc7 = AlexNet(resized, feature_extract=True)
# NOTE: `tf.stop_gradient` prevents the gradient from flowing backwards
# past this point, keeping the weights before and up to `fc7` frozen.
# This also makes training faster, less work to do!
fc7 = tf.stop_gradient(fc7)

# Add the final layer for traffic sign classification.
shape = (fc7.get_shape().as_list()[-1], nb_classes)  # use this shape for the weight matrix

fc8_weights = tf.Variable(tf.truncated_normal(shape=shape))
fc8_bias = tf.Variable(tf.truncated_normal([nb_classes]))
logits = tf.matmul(fc7, fc8_weights) + fc8_bias

# TODO: Define loss, training, accuracy operations.
# HINT: Look back at your traffic signs project solution, you may
# be able to reuse some the code.
y = tf.placeholder(tf.int32, (None))
one_hot_y = tf.one_hot(y,43)

EPOCHS = 20
BATCH_SIZE = 120
rate = 0.0009

cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=one_hot_y, logits=logits)
loss_operation = tf.reduce_mean(cross_entropy)
optimizer = tf.train.AdamOptimizer(learning_rate=rate)
training_operation = optimizer.minimize(loss_operation)
correct_prediction = tf.equal(tf.argmax(logits,1), tf.argmax(one_hot_y,1))
accuracy_operation = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

def evaluate(X_data, y_data):
    num_examples = len(y_data)
    total_accuracy = 0
    total_loss = 0
    sess = tf.get_default_session()
    for offset in range(0, num_examples, BATCH_SIZE):
        batch_x, batch_y = X_data[offset:offset+BATCH_SIZE], y_data[offset:offset+BATCH_SIZE]
        accuracy, loss = sess.run([accuracy_operation, loss_operation], feed_dict={x: batch_x, y: batch_y})
        total_accuracy += (accuracy * len(batch_x))
        total_loss += (loss * len(batch_x))
    return (total_accuracy/num_examples, total_loss/num_examples)

# Train and evaluate the feature extraction model.
# Initializing the variables
init = tf.global_variables_initializer()
saver = tf.train.Saver()
def run_session(X_train, y_train, EPOCHS, BATCH_SIZE, X_valid, y_valid):
    with tf.Session() as sess:
        sess.run(init)
        num_examples = len(X_train)

        print("Training...")
        print()
        valid_accuracy = []
        train_accuracy = []
        for i in range(EPOCHS):
            X_train, y_train = shuffle(X_train, y_train)
            for offset in range(0, num_examples, BATCH_SIZE):
                end = offset + BATCH_SIZE
                batch_x, batch_y = X_train[offset:end], y_train[offset:end]
                sess.run(training_operation, feed_dict={x: batch_x, y: batch_y})

            validation_accuracy, valid_loss = evaluate(X_valid, y_valid)
            training_accuracy, train_loss = evaluate(X_train, y_train)

            valid_accuracy.append(validation_accuracy)
            train_accuracy.append(training_accuracy)

            print("EPOCH {} ...".format(i+1))
            print("Validation Accuracy = {:.3f}".format(validation_accuracy))
            print("Training Accuracy = {:.3f}".format(training_accuracy))
            print()

        saver.save(sess, './traffic-sign-classifier')
        print("Model saved")
        
        return (train_accuracy, train_loss, valid_accuracy, valid_loss)
X_input, y_input = shuffle(X_train, y_train)
(train_accuracy, train_loss, valid_accuracy, valid_loss) = run_session(X_input, 
                                                                       y_input, 
                                                                       EPOCHS, 
                                                                       BATCH_SIZE,
                                                                       X_test, 
                                                                       y_test)