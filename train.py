import tensorflow as tf
from models.cnn import CNN
from dataloader import load_data
from tqdm import tqdm
from tensorflow.keras.utils import Progbar
import time
import math
from tqdm import tqdm

class Trainer:
    
    def __init__(self, model, loss_fn, optimizer, epochs, batch_size):
        
        self.model = model
        self.loss_fn = loss_fn
        self.optimizer = optimizer
        self.epochs = epochs
        self.batch_size = batch_size
        
    def compute_acc(self, y_pred, y):
        correct = tf.equal(tf.argmax(y_pred, -1), tf.argmax(y, -1))
        accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))
        return accuracy
    
    @tf.function
    def train_step(self, x, y):
        with tf.GradientTape() as tape:
            logits = self.model(x)
            loss = self.loss_fn(y, logits)
        grads = tape.gradient(loss, self.model.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_weights))
        
        return loss, logits
    
    def train(self, train_ds, steps_per_epoch, val_ds, val_steps, checkpoint_manager) :
        
        metrics_names = ['train_loss', 'train_acc', 'val_loss', 'val_acc']
        history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

        best_loss = 100
        for epoch in range(self.epochs):
            
            # train_ds = train_ds.shuffle(100)
            # val_ds = val_ds.shuffle(100)

            train_ds = train_ds.take(steps_per_epoch)
            val_ds = val_ds.take(val_steps)

            train_loss = tf.keras.metrics.Mean(name='train_loss')
            train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='train_accuracy')

            valid_loss = tf.keras.metrics.Mean(name='valid_loss')
            valid_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='valid_accuracy')

            progBar = Progbar(steps_per_epoch * self.batch_size, stateful_metrics=metrics_names)
            print("\nStart of epoch %d" % (epoch,))
            
            start_time = time.time()
            
            # # progBar = Progbar(steps_per_epoch * self.batch_size, stateful_metrics=metrics_names)
            # # pbar_train = tqdm(total=steps_per_epoch)
            for step_train, (x_batch, y_batch) in enumerate(train_ds):
                loss, logits = self.train_step(x_batch, y_batch)
                # train_acc = self.compute_acc(logits, y_batch)
                train_loss(loss)
                train_acc()
            #     # values = [('train_loss', train_loss.result().numpy()), ('train_acc', train_acc.result().numpy())]
                values = [('train_loss', train_loss), ('train_acc', train_acc)]
                progBar.update((step_train + 1) * self.batch_size, values=values)
                
                # if step_train % 100 == 0:
                #     print("Epoch: {}/{}, step: {}/{}, loss: {:.5f}, accuracy: {:.5f}".format(epoch + 1,
                #                                                                         self.epochs,
                #                                                                         step_train,
                #                                                                         math.ceil(train_size / self.batch_size),
                #                                                                         train_loss.result(),
                #                                                                         train_acc.result()))
            # history['train_loss'].append(train_loss)
            # history['train_acc'].append(train_acc)
            # print(f"train_loss: {history['train_loss'][-1]:.4f} - train_acc: {history['train_acc'][-1]:.4f}")
 
            # pbar_train.close()
            # if val_ds is not None:
            #     val_loss = tf.keras.metrics.Mean()
            #     val_acc = tf.keras.metrics.SparseCategoricalAccuracy()
                
            #     for step_val, (x_batch, y_batch) in enumerate(val_ds):
            #         logits = model(x_batch, training=False)
                    
            #         # batch_val_loss = self.loss_fn(y_batch, logits)
            #         # batch_val_acc = self.compute_acc(logits, y_batch)
                    
            #         val_loss(self.loss_fn(y_batch, logits))
            #         val_acc(y_batch, self.model(x_batch))
                    
            #     #     values = [('train_loss', batch_loss), ('train_acc', batch_acc), ('val_loss', batch_val_loss), ('val_acc', batch_val_acc)]
            #     # progBar.update((step_train + 1) * self.batch_size, values=values, finalize=True)   
                
            #     history['val_loss'].append(val_loss.result().numpy())
            #     history['val_acc'].append(val_acc.result().numpy())
            #     print(f"val_loss: {history['val_loss'][-1]:.4f} - val_acc: {history['val_acc'][-1]:.4f}")
            
            # print("Time taken: %.2fs" % (time.time() - start_time))
            
            # if val_loss < best_loss:
            #     best_loss = val_loss
            #     print("\nSave better model: ", end='')
            #     print(checkpoint_manager.save())
                
        # return history 
            
if __name__ == "__main__" :
    
    mnist = tf.keras.datasets.mnist
    train_ds, test_ds, val_ds, size_list =load_data(mnist)
    train_size, val_size, test_size = size_list
    
    loss_function = tf.keras.losses.SparseCategoricalCrossentropy()
    optimizer = tf.keras.optimizers.Adam()

    model = CNN(num_classes=10)
    epochs = 10
    batch_size = 32
    
    compute_steps_per_epoch = lambda x: int(math.ceil(1. * x / batch_size))
    steps_per_epoch = compute_steps_per_epoch(train_size)
    val_steps = compute_steps_per_epoch(val_size)
    
    checkpoint = tf.train.Checkpoint(optimizer=optimizer, model=model)
    checkpointmanager = tf.train.CheckpointManager(checkpoint, directory='./checkpoints', max_to_keep=5)
    
    # Trainer 클래스를 사용하여 모델 학습
    trainer = Trainer(model, loss_fn=loss_function, optimizer=optimizer, epochs=epochs, batch_size=batch_size)
    trainer.train(train_ds=train_ds, steps_per_epoch=steps_per_epoch, val_steps=val_steps, val_ds=val_ds, checkpoint_manager=checkpointmanager)
         

