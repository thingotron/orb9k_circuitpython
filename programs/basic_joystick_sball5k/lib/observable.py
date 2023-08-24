# the basic pipeline comes from the good old Observer pattern,
# but we have a wrinkle.  In order to handle even moderately
# deep pipelines in such a memory-starved environment, we change
# the nomenclature; a PipelineStage is intended to be part of a
# multistage transformation of data; at any point on that, we
# can attach an observer to report on it.

# the PipelineStages are aggregated into a Pipeline; at every
# stage *if* the stage emits a new message, the Pipeline
# gathers that, sends it to that stage's observers, and
# then iterates and sends that as the input to the next stage.

# the end result is we avoid the stack at the expense of
# elegance.

# Historically this was changed because while it was possible
# to increase the stack space in CircuitPython, it only appeared
# to have an effect after one soft reboot, which made it fail
# on initial run.  This appears to have fixed the problem.

class Observer:

    def __init__(self):
        pass

    def receive(self, msg):
        pass

class PipelineStage(Observer):

    def __init__(self):
        self.observers = []
        self.has_new_msg = False
        self.next_msg = None

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def emit(self, msg):
        # sets the next message to be put through
        # the pipeline and sets a flag so that the pipeline
        # knows to move forward.  This isn't as clean
        # as just emitting to the next stage, but it
        # avoids a stack overflow
        self.has_new_msg = True
        self.next_msg = msg

    def update_observers(self, msg):
        for observer in self.observers:
            observer.receive(msg)


class Pipeline():

    def __init__(self, stages):
        self.stages = stages

    def tick(self):
        # for each stage in the pipeline:
        msg = None
        for stage in self.stages:
            # receive a result from it
            stage.receive(msg)
            if stage.has_new_msg:
                # if the stage generated a new message
                # for all attached observers, emit to those
                stage.has_new_msg = False
                msg = stage.next_msg
                stage.update_observers(msg)
                # call the next stage in the pipeline with that result
            else:
                # otherwise, no new message and we're done
                # for this tick
                return

