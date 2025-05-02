
import random
import numpy as np
import pygame


class Agent:
    def __init__(self, pipeline_length):
        # self.position = 0  # starts at leftmost node
        self.position = random.randint(0, pipeline_length - 1)  # random spawn
        self.pipeline_length = pipeline_length
        self.action_space = ['left', 'right', 'repair']

    def step(self,actionWord, pipeline=None):
        if actionWord == 'left':
            self._move_left()
        elif actionWord == 'right':
            self._move_right()
        elif actionWord == 'repair':
            if pipeline:
                pipeline.state[self.position]["damage"] = 0
                pipeline.last_repaired = self.position


    def _move_left(self):
        if self.position > 0:
            self.position -= 1

    def _move_right(self):
        if self.position < self.pipeline_length - 1:
            self.position += 1

    # def _repair(self, pipeline):
    #     # Set damage at current position to 0
    #     pipeline.state[self.position]["damage"] = 0
    
    def sample_action(self):
        return random.choice(self.action_space)



class Pipeline():
    def __init__(self,
                num_locations=6,
                damage_probs=[0.1, 0.2, 0.3,0.4],
                initial_damage_levels=[0,1,2,2,3,1],
                render_mode = None,
                discount_factor=1.0,
                damage_costs=[0,1,3,6,10,20],
                ):
        self.last_repaired = None
        self.num_locations = num_locations
        self.discount_factor  = discount_factor
        self.tau = len(damage_probs)
        self.gamma_list = damage_probs
        self.trans_matrix = self.generate_transition_matrix_np() 
        self.state = self.initialState(num_locations,initial_damage_levels)
        self.damage_costs = damage_costs
        self.cost = sum(self.damage_costs[loc["damage"]] for loc in self.state)

        self.agent = Agent(self.num_locations)
        
        self.render_mode = render_mode
        if self.render_mode == "human":
            self.init_pygame()

        

        


    @staticmethod
    def damagePropagate(damageTransition, prevDamageLevel):
        damageLevel = prevDamageLevel
        rand_prob = random.random()
        cumulative_prob = 0
        for j in range(len(damageTransition[damageLevel])):
            cumulative_prob += damageTransition[damageLevel][j]
            if rand_prob < cumulative_prob:
                damageLevel = j
                break
        return damageLevel
    
    def generate_transition_matrix_np(self):
    
        assert len(self.gamma_list) == self.tau, "gamma_list length must match tau"
        
        matrix = np.zeros((self.tau + 1, self.tau + 1))
        matrix[0, 0] = 1.0
        for i in range(1, self.tau):
            matrix[i, i] = 1 - self.gamma_list[i]
            matrix[i, i + 1] = self.gamma_list[i]
        
        matrix[self.tau, self.tau] = 1.0

        return matrix
    
    def step(self, agent_action):
        _cost = self.cost
        self.agent.step(agent_action, self)

        cost = sum(self.damage_costs[loc["damage"]] for loc in self.state)
        self.cost = self.discount_factor * _cost + cost


        nextStateList = []
        for indState in self.state:
            prev_damage = indState["damage"]
            next_damage = self.damagePropagate(self.trans_matrix, prev_damage)
            nextStateList.append({"id" :indState["id"], "damage":next_damage})
        self.state = nextStateList
        if self.render_mode == "human":
            self.render()


    def initialState(self,num_locations,initial_damage_levels):
        stateList = []
        for indState in range(num_locations):
            stateList.append({"id" :indState, "damage":initial_damage_levels[indState] })

        return stateList
    
    def init_pygame(self, width=800, height=200):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pipeline Repair Problem")
        self.font = pygame.font.SysFont(None, 36)
        self.clock = pygame.time.Clock()
        self.render()

    def render(self):
        block_width = self.width // self.num_locations
        block_height = 50
        margin = 40

        self.screen.fill((30, 30, 30))  # Dark background

        for idx, loc in enumerate(self.state):
            x = idx * block_width + margin
            y = self.height // 2 - block_height // 2
            rect = pygame.Rect(x, y, block_width - 2 * margin, block_height)

            # Color based on damage level (simple gradient: more damage → more red)
            damage = loc["damage"]
            max_damage = self.tau
            red = int(255 * (damage / max_damage))
            green = 255 - red
            color = (red, green, 0)

            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)  # White border

            # Draw damage level number
            text = self.font.render(str(damage), True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

            # Draw agent above current position
            if idx == self.agent.position:
                agent_x = x + (block_width - 2 * margin) // 2
                agent_y = y - 20  # above the block
                pygame.draw.circle(self.screen, (0, 0, 255), (agent_x, agent_y), 10)  # blue agent

            if idx == self.last_repaired:
                color = (255, 255, 0)

        # Draw total cost at the top-left
        cost_text = self.font.render(f"Total Cost: {self.cost:.2f}", True, (255, 255, 255))
        self.screen.blit(cost_text, (10, 10))

        pygame.display.flip()
        self.clock.tick(10)  # Limit to 10 FPS
        self.last_repaired = None

    def close_pygame(self):
        pygame.quit()
    

if __name__ == "__main__":
    testPipe = Pipeline(render_mode="human")
    import ipdb; ipdb.set_trace()
    # testPipe.step()
    
    


        
        
        

    
    


    